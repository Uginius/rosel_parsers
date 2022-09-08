import json
import math
import os
from openpyxl import Workbook

from config import today
from utilites import check_dir


class TpDataToXslx:
    def __init__(self, folder):
        self.src_folder = folder
        self.data = {}
        self.workbook = Workbook()

    def run(self):
        self.load_data()
        self.fill_table()

    def load_data(self):
        folder = self.src_folder
        for filename in os.listdir(folder):
            platform = filename.split('.')[0]
            with open(f'{folder}/{filename}', 'r', encoding='utf8') as rf:
                data = json.load(rf)
                self.data[platform] = data

    def fill_table(self):
        title = ['shop', 'shop_id', 'name', 'brand', 'url', 'status', 'price', 'rating', 'feedbacks', 'need']
        self.workbook.active.append(title)
        for platform, goods in self.data.items():
            for shop_id, merch in goods.items():
                self.check_conditions(platform, int(shop_id), merch)
        result_dir = 'xls_results'
        check_dir(result_dir)
        self.workbook.save(f"{result_dir}/t_platforms_{today}.xlsx")

    def check_conditions(self, platform, shop_id, merch):
        ws = self.workbook.active
        try:
            price = float(merch['price']) if merch.get('price') else None
        except Exception as ex:
            print(ex)
            price = merch['price']
        rating = float(merch['rating']) if merch.get('rating') else None
        feedbacks = int(merch['feedbacks']) if merch.get('feedbacks') else None
        target = 4
        if rating is None:
            need = 2
        else:
            if rating > target:
                need = 0 if feedbacks > 1 else 1
            else:
                need = math.ceil(feedbacks * abs(target - rating)) if rating else 2
        prod = [platform, shop_id, merch['name'], merch['brand'], merch['url'], merch['status'], price, rating,
                feedbacks, need]
        ws.append(prod)
