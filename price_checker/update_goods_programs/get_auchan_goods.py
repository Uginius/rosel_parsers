import requests

from config import today
from logging_config import set_logging
from price_checker.prc_update_products import update_goods_folder
from ratings_trade_platforms.product import Product
from utilites import write_json

log = set_logging('price_checker')
end_link = '&apiKey=06U4652632&shuffle=true&strategy=vectors_extended,zero_queries&productsSize=20&regionId=1' \
           '&forIs=true&showUnavailable=false&withContent=false&withSku=false'
auchan_urls = [f'https://autocomplete.diginetica.net/autocomplete?st=контакт{end_link}',
               f'https://autocomplete.diginetica.net/autocomplete?st=фотон{end_link}']


def get_goods(html_list):
    products = {}
    for merch in html_list:
        cp = Product()
        cp.name = merch['name']
        cp.url = 'https://www.auchan.ru' + merch['link_url']
        cp.shop_id = int(merch['id'])
        cp.price = float(merch['price'])
        cp.trade_mark = merch['brand']
        products.update(cp.json_items())
    return products


def start_auchan_products():
    goods = {}
    for url in auchan_urls:
        print(f'*** opening {url}')
        rq = requests.get(url).json()
        products = get_goods(rq['products'])
        print(f'*** collected {len(products)} items')
        goods.update(products)
    write_json(f'{update_goods_folder}data_auchan_{today}.json', goods)


if __name__ == '__main__':
    start_auchan_products()
