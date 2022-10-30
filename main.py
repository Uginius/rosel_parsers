def product_representation_runner():
    from product_representation.main_representation import run_prre
    run_prre()


def price_checker_runner():
    from price_checker.main_price_checker import start_price_checking
    start_price_checking()


def ows_rating_runner():
    from ratings_ows.main_ows import get_wb_goods
    get_wb_goods()


def tp_runner():
    from ratings_trade_platforms.main_tp import run_trade_platforms_rating
    run_trade_platforms_rating()


def run_programs():
    # ows_rating_runner()
    # price_checker_runner()
    # product_representation_runner()
    tp_runner()


if __name__ == '__main__':
    run_programs()
