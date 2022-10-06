import json
import time
import requests
from random import randint
from config import req_headers, today
from logging_config import set_logging
from price_checker.price_checker_data_parser import get_data_from_loaded_page
from utilites import check_dir, ChromeBrowser
from threading import Thread

log = set_logging('prices_loader')


class CheckingPricePageLoader(Thread):
    instances_count = 0

    def __init__(self, platform, goods, page):
        super().__init__()
        CheckingPricePageLoader.instances_count += 1
        self.instance_order = CheckingPricePageLoader.instances_count
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
        # if self.platform != 'megastroy':  # only this platform
        #     return
        log.info(f'№{self.instance_order:2} ——— {self.platform} ——— starting')
        if self.use_selenium:
            self.browser = ChromeBrowser()
        self.get_pages()
        if self.browser:
            self.browser.close()

    def get_pages(self):
        ll = len(self.goods)
        for order, row in enumerate(self.goods, start=1):
            self.merch_id = row
            url = self.goods[row]
            shop_info = f'№{self.instance_order:2} {self.platform:>10}'
            log.info(f'{shop_info} ({order:03}/{ll:03}), row: {row}, connecting to url: {url}')
            self.get_page(url, randint(4, 9))
            self.parse_page()
        self.save_data()
        ll = len(self.collected_data)
        divider = '-' * 30
        log.info(f'{divider} {self.platform} - collected {ll} items {divider}')

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
