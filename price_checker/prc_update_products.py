from threading import Thread
from price_checker.tmp.get_auchan_goods import start_auchan_products
from price_checker.tmp.get_lenta_goods import start_getting_lenta_products
from price_checker.tmp.get_ok_goods import start_getting_ok_products
from price_checker.tmp.get_globus_goods import start_getting_globus_products
from utilites import check_dir

loaders = [
    start_getting_lenta_products,
    start_auchan_products,
    start_getting_ok_products,
    start_getting_globus_products,
]
update_goods_folder = check_dir('price_checker/update_goods_folder')


def product_loaders():
    threads = [Thread(target=foo) for foo in loaders]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


def update_goods():
    product_loaders()
