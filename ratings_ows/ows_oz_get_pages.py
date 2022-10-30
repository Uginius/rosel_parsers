import random
import time
from bs4 import BeautifulSoup
from config import today
from logging_config import set_logging
from ratings_trade_platforms.product import Product
from utilites import ChromeBrowser, check_dir, write_json

log = set_logging('ows_oz')
url_brands = {'foton': {'brand': 'ФОТОН', 'id': 'foton-138147217', 'pages': 9},
              'kontakt': {'brand': 'КОНТАКТ', 'id': 'kontakt-143268722', 'pages': 1},
              'kontakt-dom': {'brand': 'КОНТАКТ ДОМ', 'id': 'kontakt-dom-85732160', 'pages': 1},
              'safeline': {'brand': 'SafeLine', 'id': 'safeline-138147214', 'pages': 1},
              'organide': {'brand': 'Organide', 'id': 'organide-100259634', 'pages': 1},
              'rekord': {'brand': 'РЕКОРД', 'id': 'rekord-32885759', 'pages': 1},
              }


def set_urls():
    urls = []
    for brand in url_brands.values():
        brand_id = brand['id']
        pages = brand['pages']
        for order in range(1, pages + 1):
            # url = f'https://www.ozon.ru/search/?from_global=true&page={page}&seller=6793'
            page = f'page={order}&' if order > 1 else ''
            url = f'https://www.ozon.ru/brand/{brand_id}/?{page}seller=6793'
            urls.append(url)
    return urls


def collect_data(soup, brand=None):
    goods_html = soup.find('div', class_='widget-search-result-container').div
    goods = {}
    for merch in goods_html.find_all('div', recursive=False):
        if not merch.text:
            continue
        data_merch = merch.find_all(recursive=False)[1]
        merch_divs = data_merch.find_all('div', recursive=False)
        cp = Product()
        cp.trade_mark = brand
        local_a = data_merch.a
        cp.shop_id = int(local_a['href'].split('/?')[0].split('-')[-1])
        cp.name = local_a.text.strip()
        cp.url = 'https://www.ozon.ru' + local_a['href'].split('?')[0]
        try:
            md0 = merch_divs[0].text
            md1 = merch_divs[1].text
            merch_price = md1 if 'Картой' in md0 else md0
            price = merch_price.split(' ₽')[0]
            cp.price = float(''.join(price.split()))
        except Exception as ex:
            log.error(f'Cant get price #{cp.shop_id}, {cp.name}, {cp.url}, {ex}')
            cp.price = None
        len_merch_divs = len(merch_divs) - 1
        rate_box = merch_divs[len_merch_divs - 1]
        if 'продавец' in rate_box.text:
            rate_box = merch_divs[2]
        try:
            rtb = rate_box.div.div.find_all('div', recursive=False)[1]
            rating = float(rtb['style'].split(':')[1][:-2])
            cp.rating = round((5 * rating) / 100, 2)
            cp.feedbacks = int(rate_box.a.text.split()[0])
        except Exception as ex:
            log.error(f'Cant get rating #{cp.shop_id}, {cp.name}, {cp.url}, {ex}')
            cp.rating, cp.feedbacks = None, None
        pass
        goods.update(cp.json_items())
    return goods


class OzJsonBrandsGetter:
    def __init__(self):
        self.brand_links = set_urls()
        self.goods = {}
        self.cur_brands = {brand['id']: brand['brand'] for brand in url_brands.values()}
        self.cur_brand = None

    def run(self):
        self.get_pages()
        self.save_json()

    def get_pages(self):
        ll = len(self.brand_links)
        for order, url in enumerate(self.brand_links, 1):
            self.set_cur_brand(url)
            log.info(f'{order:02}/{ll}: Connect to {url}')
            self.get_and_parse_page(url, order=order)

    def get_and_parse_page(self, url, order=None):
        browser = ChromeBrowser(sandbox=True)
        browser.get(url)
        browser.scroll_down()
        time.sleep(1)
        data = {}
        try:
            data = collect_data(BeautifulSoup(browser.page_source(), 'lxml'), brand=self.cur_brand)
        except Exception as ex:
            log.error(f'{url}, {ex}')
        if data:
            self.goods.update(data)
        browser.close()
        wait_time = random.randint(3, 9)
        log.info(f'Collected {len(data)} items | sleeping {wait_time}')
        self.save_json('tmp', f'{order:02}.json', data)
        time.sleep(wait_time)

    def save_json(self, result_folder=f'raitings_ows/json_files', filename=f'oz_{today}.json', data=None):
        check_dir(result_folder)
        json_filename = f'{result_folder}/{filename}'
        if not data:
            data = self.goods
        write_json(json_filename, data)
        log.info(f'file {json_filename} saved')

    def set_cur_brand(self, url):
        for br_id in self.cur_brands:
            if br_id in url:
                self.cur_brand = self.cur_brands[br_id]
                return
        self.cur_brand = None
