import random
import time
import requests
from threading import Thread
from bs4 import BeautifulSoup
from config import today
from product_representation.src.prre_goals import oz_goals, wb_goals
from utilites import ChromeBrowser, write_json, check_dir

goals = {'oz': oz_goals, 'wb': wb_goals}


class PrRePageGetter(Thread):
    def __init__(self, shop):
        super().__init__()
        platforms_settings = {'oz': [self.oz_parser, self.oz_sender], 'wb': [self.wb_parser, self.wb_sender]}
        self.platform = shop
        self.goals = goals[shop]
        self.browser = None
        self.parser, self.sender = platforms_settings[shop]
        self.clean_data = None
        self.all_data = {}
        self.json_folder = f'product_representation/json_files/{today}'
        self.raw_data = None

    def run(self):
        print(f'{self.platform} - start to get pages ******\n', end='')
        for rq_id, rq_data in self.goals.items():
            query = rq_data['request']
            self.sender(query)
            if not self.raw_data:
                continue
            self.parser()
            self.all_data[rq_id] = self.clean_data
            ll = len(self.goals)
            print(f'{self.platform}, found {len(self.clean_data)} items, request id: {rq_id}/{ll}, query: {query}')
        self.save_json()

    def oz_parser(self):
        self.clean_data, data = None, {}
        for order, html_product in enumerate(self.raw_data, 1):
            merch = self.get_oz_elements(html_product)
            if not merch:
                break
            data[order] = merch
        self.clean_data = data

    def get_oz_elements(self, html_product):
        divs = html_product.find_all('div', recursive=False)
        try:
            link = divs[1].find('a', class_='tile-hover-target')
        except IndexError:
            return None
        if not link:
            card = divs[0]
            link = card.find('a', class_='tile-hover-target')
            seller_div = card.find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1]
            merch_seller = self.get_seller(seller_div.find_all(recursive=False)[-1].text)
        else:
            merch_seller = self.get_seller(divs[2].find_all('div', recursive=False)[-1].find_all('span')[3].text)
        merch_name = link.text.strip()
        merch_url = 'https://www.ozon.ru' + link['href'].split('/?')[0]
        merch_id = merch_url.split('-')[-1]
        if 'http' in merch_id:
            merch_id = merch_id.split('/')[-1]
        return {'brand': merch_seller, 'shop_id': merch_id, 'name': merch_name, 'url': merch_url}

    def get_seller(self, seller):
        if 'продавец' in seller:
            return seller.split('продавец ')[1]
        if seller == 'За час курьером Ozon Express':
            return 'Ozon'
        return None

    def oz_sender(self, shop_query):
        self.browser = ChromeBrowser()
        self.browser.get(f'https://www.ozon.ru/search/?text={shop_query}', wait_time=random.randint(4, 9))
        soup = BeautifulSoup(self.browser.page_source(), 'lxml')
        self.browser.close()
        try:
            product_class = soup.find('div', class_='widget-search-result-container').div.div['class']
            self.raw_data = soup.find_all('div', class_=product_class)
        except Exception as e:
            print(f'OZ product class error, query: {shop_query}.', e)
            self.raw_data = None

    def wb_sender(self, shop_query):
        rq1 = 'https://search.wb.ru/exactmatch/ru/common/v4/search?appType=1&couponsGeo=12,3,18,15,21' \
              '&curr=rub&dest=-1029256,-102269,-2162196,-1257786&emp=0&lang=ru&locale=ru&pricemarginCoeff=1.0'
        rq_query = f'&query={shop_query}'
        rq2 = '&reg=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,40,1,48,71' \
              '&resultset=catalog&sort=popular&spp=0&suppressSpellcheck=false'
        url = rq1 + rq_query + rq2 + '&resultset=catalog&sort=popular'
        try:
            response = requests.get(url)
            self.raw_data = response.json()['data']['products']
            time.sleep(random.randint(3, 7))
        except Exception as e:
            print(e)
            self.raw_data = None

    def wb_parser(self):
        self.clean_data, data = None, {}
        for order, product in enumerate(self.raw_data, 1):
            merch_id = product['id']
            merch_name = product['name']
            merch_url = f'https://www.wildberries.ru/catalog/{merch_id}/detail.aspx'
            merch_seller = product['brand']
            data[order] = {'brand': merch_seller, 'shop_id': merch_id, 'name': merch_name, 'url': merch_url}
        self.clean_data = data

    def save_json(self):
        check_dir(self.json_folder)
        write_json(f'{self.json_folder}/{self.platform}_{today}.json', self.all_data)

# url = f'https://www.ozon.ru/search/?from_global=true&page={page}&seller=6793'