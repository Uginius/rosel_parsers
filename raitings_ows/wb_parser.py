import json
import os
from openpyxl import Workbook
from bs4 import BeautifulSoup

from config import today
from utilites import ChromeBrowser, check_dir

folder = 'raitings_ows/htmls_wb'


def load_data():
    browser = ChromeBrowser()
    for page in range(1, 5):
        # url = f'https://www.wildberries.ru/seller/30766?sort=popular&page={page}'
        url = f'https://catalog.wb.ru/sellers/catalog?appType=1&couponsGeo=12,7,3,6,5,18,21&curr=rub&dest=-1216601,-337422,-1114902,-1198055&emp=0&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&reg=0&regions=68,64,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48&sort=popular&spp=0&supplier=30766'
        browser.get(url, wait_time=5)
        filename = f'{folder}/json_wb_page_{page:02}.html'
        with open(filename, 'w', encoding='utf8') as write_file:
            write_file.write(browser.page_source())


def collect_wb_json(data):
    goods = {}
    for merch in data['products']:
        id_ = merch["id"]
        goods[id_] = {
            'name': merch['name'],
            'brand': merch['brand'],
            'old_price': merch['priceU'] / 100,
            'price': merch['salePriceU'] / 100,
            'rating': merch['rating'],
            'feedbacks': merch['feedbacks'],
            'url': f'https://www.wildberries.ru/catalog/{id_}/detail.aspx'
        }
    return goods


def files_to_json():
    json_files = os.listdir(folder)
    wb_products = {}
    for filename in json_files:
        with open(f'{folder}/{filename}', 'r', encoding='utf8') as read_file:
            soup = BeautifulSoup(read_file.read(), 'lxml')
        data = collect_wb_json(json.loads(soup.find('pre').text)['data'])
        wb_products.update(data)
    return wb_products


def make_xls_file(data):
    wb = Workbook()
    ws = wb.active
    title = ['wb_id', 'name', 'brand', 'url', 'price', 'rating', 'feedbacks']
    ws.append(title)
    for wb_id, p in data.items():
        prod = [wb_id, p['name'], p['brand'], p['url'], p['price'], p['rating'], p['feedbacks']]
        ws.append(prod)
    result_dir = 'xls_results'
    check_dir(result_dir)
    wb.save(f"{result_dir}/wb_data_{today}.xlsx")


def wb_data_getter():
    data = files_to_json()
    make_xls_file(data)
