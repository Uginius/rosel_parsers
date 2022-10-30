from logging_config import set_logging
from utilites import time_track, id_url_from_table

actual_table = 'price_checker/src_checker/actual.xlsx'
log = set_logging('price_checker')


@time_track
def get_pages(page):
    from price_checker.checker_utilites import divide_goods_by_platforms
    from price_checker.price_checker_get_data_from_web import CheckingPricePageLoader
    platform_links = divide_goods_by_platforms(id_url_from_table(actual_table, page))
    getters = [CheckingPricePageLoader(platform, goods, page) for platform, goods in platform_links.items()]
    log.info(f'★★★ Price checker started with {len(getters)} platforms ★★★')
    for getter in getters:
        getter.start()
    for getter in getters:
        getter.join()


@time_track
def create_result_xls_from_json():
    from price_checker.price_checker_xlsx_from_jsons import JsonPriceToXls
    res = JsonPriceToXls(actual_table)
    res.run()


@time_track
def start_updating_products():
    from price_checker.checker_utilites import shops_for_update_data
    from price_checker.update_goods_programs.prc_goods_data_updater import PricesDataUpdater
    from price_checker.update_goods_programs.table_from_updated_goods import create_table_from_updated_goods
    log.info(f'★★★ Update data started with {len(shops_for_update_data)} platforms ★★★')
    data_updaters = [PricesDataUpdater(shop) for shop in shops_for_update_data]
    for updater in data_updaters:
        updater.start()
    for updater in data_updaters:
        updater.join()
    create_table_from_updated_goods()


def start_price_checking():
    # start_updating_products()
    get_pages('rosel')
    get_pages('oppo')
    create_result_xls_from_json()
