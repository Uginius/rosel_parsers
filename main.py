from price_checker.main_price_checker import start_price_checking
from product_representation.main_representation import run_prre
from raitings_ows.main_ows import get_wb_goods
from ratings_trade_platforms.main_tp import run_trade_platforms_rating


def run_programs():
    # get_wb_goods()
    # run_trade_platforms_rating()
    # run_prre()
    start_price_checking()


if __name__ == '__main__':
    run_programs()
