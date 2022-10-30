import time
from random import randint
from threading import Thread
from bs4 import BeautifulSoup
from config import today
from logging_config import set_logging
from ratings_trade_platforms.product import Product
from utilites import append_json, check_dir, write_json
from vpn.crome2 import Chrome2

log = set_logging('ows')


class OzDataLoader(Thread):
    instances_count = 0

    def __init__(self, proxy, data):
        super().__init__()
        OzDataLoader.instances_count += 1
        self.instance_order = OzDataLoader.instances_count
        self.result = {}
        self.browser = Chrome2(sandbox=True, proxy_passless=proxy)
        self.src_data = data
        self.order = None
        self.soup = None
        self.goods_shop_id = None
        self.cp = None
        self.proxy = proxy
        self.json_filename = f'{check_dir("ratings_ows/json_files")}/oz_{self.instance_order}_{today}.json'

    def run(self):
        ll = list(self.src_data.keys())[-1]
        for order, product in self.src_data.items():
            self.set_cp_from_src(product, order)
            log.info(f'{order}/{ll}, {self.proxy:20}: Connect to {self.cp.url}')
            self.get_page()
            if self.status_not_in_sale():
                self.update_results()
                continue
            self.get_review_url()
            self.get_price()
            self.update_results()
            write_json(self.json_filename, self.result)

    def update_results(self):
        data = self.cp.json_items()
        append_json(f'{check_dir("ratings_ows/tmp")}/oz_{today}.json', data)
        self.result.update(data)

    def set_cp_from_src(self, product, order):
        cp = Product()
        cp.order = order
        cp.name = product['name']
        cp.rosel_id = product['rosel_id']
        cp.shop_id = product['shop_id']
        cp.url = product['url']
        cp.trade_mark = product['trade_mark']
        self.cp = cp

    def get_page(self):
        url = self.cp.url
        try:
            self.browser.get(url)
        except Exception as ex:
            log.error(f'order: {self.order}, url: {url}, {ex}')
        wait_time = randint(3, 8)
        time.sleep(wait_time)
        self.soup = BeautifulSoup(self.browser.page_source(), 'lxml')

    def get_review_url(self):
        try:
            review_prod = self.soup.find('div', attrs={'data-widget': 'webReviewProductScore'})
            a = review_prod.a
            review_url = 'https://www.ozon.ru' + a['href']
            self.cp.review_url = review_url
            self.get_reviews(review_prod)
        except Exception as ex:
            log.error(f'Cant get review url, {ex}')

    def status_not_in_sale(self):
        not_in_sale = False
        status = 'Этот товар закончился'
        try:
            h2 = self.soup.find('h2').text
            if status in h2:
                not_in_sale = True
                self.cp.status = status
                log.error(f'raw {self.cp.order}, product not in sale')
        except Exception:
            not_in_sale = False
        return not_in_sale

    def get_reviews(self, review_prod):
        cp = self.cp
        try:
            review_block = review_prod.div.div.div.div
            rtb = review_block.find_all('div', recursive=False)[1]
            cp.rating = round(float(rtb['style'].split(':')[1][:-2]) * 0.05, 2)
            cp.feedbacks = int(review_prod.a.text.split()[0])
        except Exception as ex:
            log.error(f'Review getting error. Row: {cp.order}, {ex}')

    def get_price(self):
        try:
            price_block = self.soup.find('div', attrs={'data-widget': 'webPrice'}).text
            price = price_block.split('₽')[0].split()
            self.cp.price = float(''.join(price))
        except Exception as ex:
            log.error(f'Price getting error. Row: {self.cp.order}, {ex}')


def run_oz_data_loading(data):
    pass
    data_loader = OzDataLoader(data)
    data_loader.run()

    # 'https://www.ozon.ru/context/detail/id/316021548/reviews/'
