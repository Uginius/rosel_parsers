from product_representation.prre_monthly_data_analytics import PrReMonthlyDataAnalytics
from product_representation.prre_products_getter import PrRePageGetter
from utilites import time_track

wb_search = False
oz_search = True
prre_platforms = ['wb' if wb_search else None, 'oz' if oz_search else None]


@time_track
def get_prre_pages():
    getters = [PrRePageGetter(shop) for shop in prre_platforms if shop]
    for getter in getters:
        getter.run()
    for getter in getters:
        if getter.is_alive():
            getter.join()


@time_track
def prre_convert_json_to_tables():
    res = PrReMonthlyDataAnalytics()
    res.run()


def run_prre():
    # get_prre_pages()
    prre_convert_json_to_tables()
