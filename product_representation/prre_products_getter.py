import random
import time
import requests
from threading import Thread
from bs4 import BeautifulSoup
from config import today, cur_month
from logging_config import set_logging
from product_representation.src.prre_goals import oz_goals, wb_goals
from utilites import write_json, check_dir, ChromeBrowser
from vpn.crome2 import Chrome2
from vpn.sequre import ips

goals = {'oz': oz_goals, 'wb': wb_goals}
logs_name = 'pre_logs'
log = set_logging(logs_name, write_errors=True)


def get_seller(seller):
    if 'продавец' in seller:
        return seller.split('продавец ')[1]
    if seller == 'За час курьером Ozon Express':
        return 'Ozon'
    return None


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
        self.json_folder = check_dir(f'product_representation/json_files/{cur_month}')
        self.raw_data = None
        self.proxy = None

    def run(self):
        self.get_pages(self.goals)
        self.check_errors()
        self.save_json()

    def get_pages(self, src_data, msg='start to get pages ******'):
        log.info(f'{self.platform} - {msg}')
        for rq_id, rq_data in src_data.items():
            ll = len(src_data)
            query = rq_data['request']
            self.sender(query)
            if not self.raw_data:
                continue
            request_id = f'request id: {rq_id}/{ll}'
            try:
                self.parser()
                q_products = len(self.clean_data)
                if q_products == 4:
                    raise Exception('Only 4 items found')
                self.all_data[rq_id] = self.clean_data
                log.info(f'{self.platform}, found {q_products :3}, {request_id}, query: {query}, proxy: {self.proxy}')
            except Exception as e:
                log.error(f'[{self.platform}], {request_id}, query: {query}, ERROR: {e}')
        log.info(f'****** {self.platform} - data collected')

    def check_errors(self):
        log_filename = f'logs/{logs_name}.log'
        goals_errors_ids = []
        with open(log_filename, 'r', encoding='utf8') as rf:
            for line in rf:
                if 'ERROR' in line:
                    platform = line.split('| [')[1].split(']')[0]
                    if platform != self.platform:
                        continue
                    rq_id = line.split('id: ')[1].split('/')[0]
                    goals_errors_ids.append(rq_id)
        if goals_errors_ids:
            self.get_selected_rqs(goals_errors_ids)

    def get_selected_rqs(self, rqs_ids):
        goal_to_rq = {}
        for rq_id in rqs_ids:
            goal_to_rq[rq_id] = self.goals[rq_id]
        q_ids = len(rqs_ids)
        self.get_pages(goal_to_rq, msg=f'Trying to get {q_ids} pages ******')

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
            merch_seller = get_seller(seller_div.find_all(recursive=False)[-1].text)
        else:
            merch_seller = get_seller(divs[2].find_all('div', recursive=False)[-1].find_all('span')[3].text)
        merch_name = link.text.strip()
        merch_url = 'https://www.ozon.ru' + link['href'].split('/?')[0]
        merch_id = merch_url.split('-')[-1]
        if 'http' in merch_id:
            merch_id = merch_id.split('/')[-1]
        return {'brand': merch_seller, 'shop_id': merch_id, 'name': merch_name, 'url': merch_url}

    def get_data_from_browser(self, url):
        self.browser = Chrome2(sandbox=True, proxy_passless=self.proxy)
        try:
            self.browser.get(url)
            soup = BeautifulSoup(self.browser.page_source(), 'lxml')
        except Exception as e:
            log.error(f'[{self.platform}] error getting data from browser, {e}')
            soup = None
        if self.browser:
            self.browser.close()
        return soup

    def oz_sender(self, shop_query):
        self.proxy = ips.pop(0)
        ips.append(self.proxy)
        url = f'https://www.ozon.ru/search/?text={shop_query}'
        soup = self.get_data_from_browser(url)
        try:
            product_class = soup.find('div', class_='widget-search-result-container').div.div['class']
            self.raw_data = soup.find_all('div', class_=product_class)
        except Exception as e:
            log.error(f'OZ product class error, query: {shop_query}. {e}')
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
            log.error(e)
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
        json_filename = f'{self.json_folder}/{self.platform}_{today}.json'
        write_json(json_filename, self.all_data)
        log.info(f'{json_filename} saved')


# url = f'https://www.ozon.ru/search/?from_global=true&page={page}&seller=6793'

if __name__ == '__main__':
    data = ['oz019', 'oz045']
    oz_getter = PrRePageGetter('oz')
    oz_getter.get_selected_rqs(data)
    oz_getter.save_json()
