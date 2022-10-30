from threading import Thread
import requests
from bs4 import BeautifulSoup
from config import today
from logging_config import set_logging
from price_checker.checker_utilites import shops_for_update_data
from price_checker.update_goods_programs.data_links import urls_lnt, urls_ach, urls_glo, urls_oke
from ratings_trade_platforms.product import Product
from utilites import write_json, check_dir
from vpn.crome2 import Chrome2

urls = {'ach': urls_ach, 'glo': urls_glo, 'lnt': urls_lnt, 'oke': urls_oke}
update_goods_folder = check_dir('price_checker/updated_goods_folder/')
log = set_logging('price_checker')


class PricesDataUpdater(Thread):
    instances_count = 0

    def __init__(self, shop):
        super().__init__()
        PricesDataUpdater.instances_count += 1
        self.instance_order = PricesDataUpdater.instances_count
        self.shop_sign = shop
        self.platforms_json = ['ach']
        self.platforms_chrome = ['glo', 'lnt', 'oke']
        self.page_products = None
        self.goods = {}
        self.browser = None
        self.soup_or_rq = None

    def run(self) -> None:
        shop = self.shop_sign
        platform = f'№{self.instance_order:02}—{shops_for_update_data[shop]}'
        log.info(f'{platform} ——— starting')
        if shop in self.platforms_chrome:
            sandbox = True if shop in ['glo', 'lnt', 'oke'] else False
            self.browser = Chrome2(sandbox=sandbox)
        for url in urls[shop]:
            log.info(f'{platform} *** opening {url}')
            try:
                self.get_url(url)
                self.goods.update(self.page_products)
                log.info(f'{platform} *** collected {len(self.page_products)} items')
            except Exception as ex:
                log.error(f'{platform}, error getting page, {ex}')
        json_filename = f'{update_goods_folder}data_{shop}_{today}.json'
        write_json(json_filename, self.goods)
        log.info(f'{platform} collecting data finished, {json_filename} saved')
        if self.browser:
            self.browser.close()
        log.info(f'')

    def get_url(self, url):
        self.soup_or_rq = None
        if self.shop_sign in self.platforms_chrome:
            self.browser.get(url)
            self.soup_or_rq = BeautifulSoup(self.browser.page_source(), 'lxml')
        elif self.shop_sign in self.platforms_json:
            self.soup_or_rq = requests.get(url).json()
        self.parse_browser_data()

    def parse_browser_data(self):
        self.page_products = {}
        soup = self.soup_or_rq
        match self.shop_sign:
            case 'ach':
                self.get_ach_goods(soup['products'])
            case 'glo':
                self.get_glo_goods(soup.find_all('div', class_='catalog-section__item catalog-section__item--main'))
            case 'lnt':
                self.get_lnt_goods(soup.find_all('div', class_='sku-card-small-container'))
            case 'oke':
                self.get_oke_goods(soup.find_all('div', class_='product ok-theme'))

    def get_ach_goods(self, html_list):
        for merch in html_list:
            cp = Product()
            cp.name = merch['name']
            cp.url = 'https://www.auchan.ru' + merch['link_url']
            cp.shop_id = int(merch['id'])
            cp.price = float(merch['price'])
            cp.trade_mark = merch['brand']
            self.page_products.update(cp.json_items())

    def get_glo_goods(self, html_list):
        for prod in html_list:
            cp = Product()
            link = prod.a
            cp.name = link.span.text.strip()
            cp.url = 'https://online.globus.ru' + prod.a['href']
            cp.shop_id = cp.url.split('/')[-2]
            price_box = prod.find('span', class_='catalog-section__item-info')
            rub = price_box.find('span', class_='item-price__rub').text.split()
            kop = price_box.find('span', class_='item-price__kop').text.strip()
            cp.price = float(f'{"".join(rub)}.{kop}')
            self.page_products.update(cp.json_items())

    def get_lnt_goods(self, html_list):
        for prod in html_list:
            cp = Product()
            cp.name = prod.find('div', class_='sku-card-small-header__title').text.strip()
            cp.url = 'https://lenta.com' + prod.a['href']
            cp.shop_id = cp.url.split('-')[-1][:-1]
            cp.rating = float(prod.find('span', class_='sku-card-small-header__rating-text').text)
            cp.feedbacks = int(prod.find('span', class_='sku-card-small-header__comments-text').text)
            try:
                cp.price = float(prod.find('span', class_='price-label__integer').text)
            except Exception as ex:
                cp.price = None
                cp.status = prod.find('div', class_='sku-card-small__not-available-notice').text.strip()
                print(f'Cant get price, {ex}')
            self.page_products.update(cp.json_items())

    def get_oke_goods(self, html_list):
        for prod in html_list:
            cp = Product()
            link = prod.a
            cp.name = link.text.strip()
            cp.url = 'https://www.okeydostavka.ru' + prod.a['href']
            cp.shop_id = int(prod['data-catentry-id'])
            price_box = prod.find('div', class_='product-price')
            price_label = price_box.find('span', class_='price label label-red')
            if not price_label:
                price_label = price_box.find('span', class_='price label')
            price = price_label.text.split('₽')[0].replace(',', '.').split()
            cp.price = float(''.join(price))
            self.page_products.update(cp.json_items())
