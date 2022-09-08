import time
import urllib.parse
from threading import Thread
from bs4 import BeautifulSoup
from config import today
from ratings_trade_platforms.all_parsers import tp_parser
from ratings_trade_platforms.tp_config import search_phrases, blocklist, brand_list
from utilites import check_dir, ChromeBrowser, write_json


class PageGetter(Thread):
    instances_count = 0

    def __init__(self, platform):
        super().__init__()
        PageGetter.instances_count += 1
        self.instance_order = PageGetter.instances_count
        self.shop = platform
        self.folder = f'ratings_trade_platforms/all_products/{today}'
        self.phrases = set(search_phrases) - set(blocklist[platform])
        self.cur_phrase = None
        self.browser = None
        self.current_url = None
        self.has_pagination = 0
        self.page_pos = 0
        self.soup = None
        self.parser = tp_parser[platform]
        self.goods = {}
        self.goods_list = None

    def run(self):
        # if self.shop != 'votonia':
        #     return
        print(f'№{self.instance_order} {self.shop} - start to get pages ******\n', end='')
        self.browser = ChromeBrowser()
        for self.cur_phrase in self.phrases:
            self.has_pagination = 0
            self.page_pos = 0
            self.get_first_page()
            if self.has_pagination:
                self.get_other_pages()
        check_dir(self.folder)
        write_json(f'{self.folder}/{self.shop}.json', self.goods)
        print(f'****** №{self.instance_order} {self.shop} finished. Collected {len(self.goods)} products')

    def get_first_page(self):
        self.get_page()
        if self.shop == 'dns':
            time.sleep(10)
        self.parse_page()
        try:
            self.get_last_page_number()
        except Exception as ex:
            print(f'{self.shop}, getting last page number error...', ex)
            self.has_pagination = 0

    def get_other_pages(self):
        for self.page_pos in range(2, self.has_pagination + 1):
            self.get_page()
            self.parse_page()

    def get_page(self):
        self.generate_url()
        self.browser.get(url=self.current_url)
        self.browser.scroll_down()

    def generate_url(self):
        pos = self.page_pos
        query = urllib.parse.quote_plus(self.cur_phrase, safe='', encoding=None, errors=None)
        match self.shop:
            case 'akson':
                url = f'https://akson.ru/search/?q={query}'
            case 'baucenter':
                pagination = f'&PAGEN_1={pos}' if pos > 1 else ''
                url = f'https://baucenter.ru/search/?q={query}&s={pagination}'
            case 'dns':
                end = f'&p={pos}' if pos > 1 else ''
                url = f'https://www.dns-shop.ru/search/?q={query}{end}'
            case 'maxidom':
                link = f'https://www.maxidom.ru/search/catalog/?q={query}&category_search=0&amount=12'
                url = link + f'&PAGEN_2={pos}' if pos > 1 else link
            case 'sdvor':
                url = f'https://www.sdvor.com/moscow/search/{query}'
            case 'votonia':
                pagination = f'/?page={pos}' if pos > 1 else ''
                url = f'https://www.votonia.ru/search/{query}{pagination}'
            case _:
                url = ''
        self.current_url = url
        pag = self.has_pagination if self.has_pagination else 'FF'
        print(f'№{self.instance_order} {self.shop:<9} {self.cur_phrase:8} {pos:02}/{pag :02}, connect to {url}')

    def parse_page(self):
        self.soup = BeautifulSoup(self.browser.page_source(), 'lxml')
        try:
            self.get_goods_list()
        except Exception as ex:
            print('Goods list loading error', ex)
        if self.goods_list:
            for html_product in self.goods_list:
                cp = self.parser(html_product)
                if not cp:
                    continue
                if not cp.trade_mark:
                    continue
                if cp.trade_mark.upper() not in brand_list:
                    continue
                if cp.url:
                    self.goods.update(cp.json_items())

    def get_last_page_number(self):
        match self.shop:
            case 'baucenter':
                self.has_pagination = int(self.soup.find('nav', class_='pagination').find_all('a')[-2].text)
            case 'dns':
                pag_block = self.soup.find('ul', class_='pagination-widget__pages')
                self.has_pagination = int(pag_block.find_all('li')[-1]['data-page-number'])
            case 'maxidom':
                li = self.soup.find('div', class_='pager-catalogue__search').find_all('li')
                self.has_pagination = int(li[-2].text.strip())
            case 'votonia':
                self.has_pagination = 3
            case _:
                self.has_pagination = 0

    def get_goods_list(self):
        soup = self.soup
        self.goods_list = None
        match self.shop:
            case 'akson':
                html_goods = soup.find('div', class_='goods-list__content')
                self.goods_list = html_goods.find_all('div', class_='product-matrix goods-list__matrix')
            case 'baucenter':
                catalog = soup.find('div', class_='catalog-list')
                self.goods_list = catalog.find_all('div', class_='catalog_item with-tooltip')
            case 'dns':
                self.goods_list = soup.find_all('div', attrs={'data-id': 'product'})
            case 'sdvor':
                self.goods_list = soup.find_all('sd-product-grid-item', class_='product-grid-item')
            case 'maxidom':
                self.goods_list = soup.find('div', class_='item-list-inner').find_all('article')
            case 'votonia':
                self.goods_list = self.soup.find_all('div', class_='wfloat cat_product_box is-product')
            case _:
                self.goods_list = None

