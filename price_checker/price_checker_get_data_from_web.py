import json
import time
import requests
from random import randint
from config import req_headers, today
from price_checker.price_checker_data_parser import get_data_from_loaded_page
from utilites import check_dir, ChromeBrowser
from threading import Thread


class CheckingPricePageLoader(Thread):
    def __init__(self, platform, goods, page):
        super().__init__()
        self.platform = platform
        self.goods = goods
        self.use_selenium = platform in ['dns', 'petrovich', 'megastroy']
        self.cur_html_data = None
        self.browser = None
        self.search_id = None
        self.page = page
        self.merch_id = None
        self.collected_data = {}

    def run(self):
        # if self.platform != 'dns':  # only this platform
        #     return
        if self.use_selenium:
            try:
                self.browser = ChromeBrowser()
            except Exception as e:
                print(f'{self.platform} Browser Error', e)
                self.browser = None
        self.get_pages()
        if self.browser:
            self.browser.close()

    def get_pages(self):
        ll = len(self.goods)
        for order, row in enumerate(self.goods, start=1):
            self.merch_id = row
            url = self.goods[row]
            wait = randint(4, 9)
            shop_info = f'{self.platform:>10}'
            print(f'{shop_info} ({order:03}/{ll:03}), row: {row}, wait: {wait} | connecting to url: {url}')
            self.get_page(url, wait)
            self.parse_page()
        self.save_data()
        ll = len(self.collected_data)
        print('-' * 30, f'{self.platform} - collected {ll} items', '-' * 30, '\n')

    def get_page(self, url, wait_time):
        if self.use_selenium:
            self.browser.get(url=url)
            # self.browser.scroll_down()
            time.sleep(wait_time)
            self.cur_html_data = self.browser.page_source()
        else:
            req = requests.get(url, headers=req_headers)
            time.sleep(wait_time)
            self.cur_html_data = req.text

    def parse_page(self):
        price_json = get_data_from_loaded_page(self.cur_html_data, self.merch_id, self.platform)
        self.collected_data[self.merch_id] = price_json

    def save_data(self):
        folder = f'price_checker/web_data/{today}'
        check_dir(folder)
        filename = f'{folder}/{self.platform}_{self.page}.json'
        with open(filename, 'w', encoding='utf8') as fp:
            json.dump(self.collected_data, fp, ensure_ascii=False, indent=4)
