import os
from openpyxl import Workbook

from config import today
from price_checker.checker_utilites import shops_for_update_data
from utilites import load_json, check_dir


def load_json_files():
    folder = 'price_checker/updated_goods_folder'
    data = {}
    for filename in os.listdir(folder):
        data.update(load_json(f'{folder}/{filename}'))
    return data


def get_shop(url):
    # 'https://www.auchan.ru/product/kley-obuvnoy-kontakt-vodostoykiy-30-ml/'
    # 'https://online.globus.ru/products/izolenta-rekord-15-20-tsvet-chernyy/'
    # 'https://lenta.com/product/539923-kitajj-539923/'
    # 'https://www.okeydostavka.ru/msk/avto-dom-sad-otdykh/elektrotovary/aksessuary-dlia-doma/svetil-nik-nochnik-svetodiodnyi-setevoi-foton-nm-100l'
    for shop in shops_for_update_data.values():
        if shop in url:
            return shop


def convert_data_to_xls(data):
    wb = Workbook()
    ws = wb.active
    for shop_id, product in data.items():
        shop = get_shop(product['url'])
        line = [None, shop, None, None, product['name'], product['url'], product['price']]
        ws.append(line)
    folder = check_dir('price_checker/tmp')
    wb.save(f'{folder}/updated_{today}.xlsx')


def create_table_from_updated_goods():
    convert_data_to_xls(load_json_files())
