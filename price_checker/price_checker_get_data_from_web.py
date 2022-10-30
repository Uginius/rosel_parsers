import time
import requests
from random import randint
from config import req_headers, today
from logging_config import set_logging
from price_checker.price_checker_data_parser import get_data_from_loaded_page
from utilites import check_dir, write_json
from threading import Thread
from vpn.crome2 import Chrome2

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
        shop = self.platform
        # if shop != 'megastroy':  # only this platform
        #     return
        instance = f'№{self.instance_order:02}—{shop:*<10}'
        log.info(f'{instance} — starting')
        if self.use_selenium:
            sandbox = True if shop in ['dns', 'megastroy'] else False
            self.browser = Chrome2(sandbox=sandbox)
        self.get_pages()
        if self.browser:
            self.browser.close()

    def get_pages(self):
        shop = self.platform
        ll = len(self.goods)
        instance = f'№{self.instance_order:02}—{shop :*<10}'
        for order, row in enumerate(self.goods, start=1):
            self.merch_id = row
            url = self.goods[row]
            log.info(f'{instance} ({order:03}/{ll:03}), row: {row}, connecting to url: {url}')
            self.get_page(url, randint(4, 9))
            self.parse_page()
        filename = f'{check_dir(f"price_checker/web_data/{today}")}/{shop}_{self.page}.json'
        write_json(filename, self.collected_data)
        ll = len(self.collected_data)
        log.info(f'★ {instance} — collected {ll} items, {filename} saved')

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
