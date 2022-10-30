import os
from datetime import datetime
from openpyxl.workbook import Workbook
from config import date_template
from logging_config import set_logging
from utilites import load_json, check_dir

log = set_logging('ows_xlsx')
json_folder = 'ratings_ows/json_files'


def select_last_date_files():
    json_dates = {}
    for filename in os.listdir(json_folder):
        date = datetime.strptime(filename[3:-5], date_template)
        if json_dates.get(date):
            json_dates[date].append(filename)
        else:
            json_dates[date] = [filename]
    last_date = sorted(list(json_dates))[-1]
    return last_date.strftime(date_template), json_dates[last_date]


def make_xls_file():
    last_date, last_files = select_last_date_files()
    wb = Workbook()
    for json_filename in last_files:
        shop = json_filename[:2]
        data = load_json(f'{json_folder}/{json_filename}')
        wb.create_sheet(shop)
        ws = wb[shop]
        title = ['shop_id', 'name', 'brand', 'url', 'price', 'rating', 'feedbacks']
        ws.append(title)
        for shop_id, p in data.items():
            try:
                price = float(p['price'])
            except Exception as ex:
                log.error(f'[{shop}] Price error, {ex}, {p["url"]}')
                price = None
            prod = [int(shop_id), p['name'], p['brand'], p['url'], price, p['rating'], p['feedbacks']]
            ws.append(prod)
    wb.remove(wb['Sheet'])
    wb.save(f'{check_dir("xls_results/ows")}/ows_{last_date}.xlsx')


def convert_jsondata_to_xls():
    make_xls_file()
