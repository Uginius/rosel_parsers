import time

import requests
from config import today
from logging_config import set_logging
from ratings_trade_platforms.product import Product
from utilites import write_json, check_dir

log = set_logging('ows_wb')


def set_urls():
    urls = []
    p1 = 'https://catalog.wb.ru/sellers/catalog?appType=1&couponsGeo=12,7,3,6,5,18,21&curr=rub'
    p1 = p1 + '&dest=-1216601,-337422,-1114902,-1198055&emp=0&lang=ru&locale=ru'
    p3 = '&pricemarginCoeff=1.0&reg=0&regions=68,64,83,4,38,80,33,70,82,86,30,69,1,48,22,66,31,40&spp=0&supplier=30766'
    for page in range(1, 5):
        p2 = f'&page={page}' if page > 1 else ''
        urls.append(p1 + p2 + p3)
    return urls


class WbJsonBrandsGetter:
    def __init__(self):
        self.brand_links = set_urls()
        self.goods = {}

    def run(self):
        self.get_pages()
        self.save_json()

    def get_pages(self):
        for url in self.brand_links:
            log.info(f'Connect to {url}')
            self.get_wb_json_page(url)

    def get_wb_json_page(self, url):
        rq = requests.get(url)
        products = rq.json()['data']['products']
        goods = {}
        for merch in products:
            cp = Product()
            wb_id = merch['id']
            cp.name = merch['name']
            cp.rating = float(merch['rating'])
            cp.feedbacks = merch['feedbacks']
            cp.price = merch['salePriceU'] / 100
            cp.trade_mark = merch['brand']
            cp.shop_id = wb_id
            cp.url = f'https://www.wildberries.ru/catalog/{wb_id}/detail.aspx'
            goods.update(cp.json_items())
        log.info(f'collected {len(goods)} items')
        self.goods.update(goods)
        time.sleep(1)

    def save_json(self):
        folder = f'ratings_ows/json_files'
        check_dir(folder)
        json_filename = f'{folder}/wb_{today}.json'
        write_json(json_filename, self.goods)
        log.info(f'file {json_filename} saved')


if __name__ == '__main__':
    wb_getter = WbJsonBrandsGetter()
    wb_getter.run()
