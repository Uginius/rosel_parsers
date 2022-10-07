from openpyxl.workbook import Workbook
from config import today
from logging_config import set_logging
from utilites import load_json, check_dir

log = set_logging('ows_xlsx')
json_folder = 'raitings_ows/json_files'


def select_last_date_files():
    return ['oz_2022-10-07.json', 'wb_2022-10-07.json']


def make_xls_file():
    last_files = select_last_date_files()
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
    result_dir = 'xls_results/ows'
    check_dir(result_dir)
    wb.save(f"{result_dir}/ows_{today}.xlsx")


def convert_jsondata_to_xls():
    make_xls_file()
