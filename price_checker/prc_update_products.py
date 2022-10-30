from threading import Thread
from price_checker.update_goods_programs.get_auchan_goods import start_auchan_products
from price_checker.update_goods_programs.get_globus_goods import start_getting_globus_products
from price_checker.update_goods_programs.get_lenta_goods import start_getting_lenta_products
from price_checker.update_goods_programs.get_ok_goods import start_getting_ok_products
from price_checker.update_goods_programs.prc_goods_data_updater import PricesDataUpdater

loaders = [
    start_getting_lenta_products,
    start_auchan_products,
    start_getting_ok_products,
    # start_getting_globus_products,
]
shops = ['lenta']


def product_loaders():
    data_updaters = [PricesDataUpdater(shop) for shop in shops]
    for updater in data_updaters:
        updater.start()
    for updater in data_updaters:
        updater.join()


def update_goods():
    product_loaders()
