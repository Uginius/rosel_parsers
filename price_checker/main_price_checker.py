from logging_config import set_logging
from price_checker.checker_utilites import divide_goods_by_platforms
from price_checker.price_checker_get_data_from_web import CheckingPricePageLoader
from price_checker.price_checker_xlsx_from_jsons import JsonPriceToXls
from price_checker.tmp.get_lenta_goods import start_getting_lenta_products
from utilites import time_track, id_url_from_table

actual_table = 'price_checker/src_checker/actual.xlsx'
log = set_logging('prices_loader')


@time_track
def get_pages(page):
    platform_links = divide_goods_by_platforms(id_url_from_table(actual_table, page))
    getters = [CheckingPricePageLoader(platform, goods, page) for platform, goods in platform_links.items()]
    log.info(f'★★★ Price checker started with {len(getters)} platforms ★★★')
    for getter in getters:
        getter.start()
    for getter in getters:
        getter.join()


@time_track
def create_result_xls_from_json():
    res = JsonPriceToXls(actual_table)
    res.run()


def start_price_checking():
    get_pages('rosel')
    get_pages('oppo')
    create_result_xls_from_json()
    # start_getting_lenta_products()
