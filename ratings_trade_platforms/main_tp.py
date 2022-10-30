from config import shops
from utilites import time_track, get_last_dir


@time_track
def get_tp_goods():
    from ratings_trade_platforms.tp_all_goods_gettet import PageGetter
    pages_from_shop_list = [PageGetter(platform) for platform in shops]
    for page in pages_from_shop_list:
        page.start()
    for page in pages_from_shop_list:
        page.join()


@time_track
def convert_tp_goods_to_xls():
    from ratings_trade_platforms.all_products.tp_data_to_xls import TpDataToXslx
    all_folder = 'ratings_trade_platforms/all_products'
    data_converter = TpDataToXslx(f'{all_folder}/{get_last_dir(all_folder)}')
    data_converter.run()


def run_trade_platforms_rating():
    get_tp_goods()
    # convert_tp_goods_to_xls()
