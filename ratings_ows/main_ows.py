from ratings_ows.src_data.load_oz_data import load_oz_xls_data
from utilites import time_track
from vpn.sequre import ips


@time_track
def ows_get_wb_pages():
    from ratings_ows.ows_wb_get_pages import WbJsonBrandsGetter
    wb_getter = WbJsonBrandsGetter()
    wb_getter.run()


@time_track
def ows_get_oz_pages():
    from ratings_ows.ows_oz_get_pages import OzJsonBrandsGetter
    oz_getter = OzJsonBrandsGetter()
    oz_getter.run()


@time_track
def collect_json_to_xls():
    from ratings_ows.ows_collect_jsondata_to_xlsx import convert_jsondata_to_xls
    convert_jsondata_to_xls()


@time_track
def oz_goods_data_loader():
    from ratings_ows.src_data.load_oz_data import load_oz_xls_data
    from ratings_ows.oz_src_data_loader import run_oz_data_loading
    xlsx_filename = 'ratings_ows/src_data/rosel_goods_OZ.xlsx'
    data = load_oz_xls_data(xlsx_filename)
    print(f'{len(data)} items loaded from {xlsx_filename}')
    run_oz_data_loading(data)


@time_track
def oz_proxy_data_loader():
    from ratings_ows.oz_src_data_loader import OzDataLoader
    data = load_oz_xls_data('ratings_ows/src_data/rosel_goods_OZ.xlsx')
    separated_data = {}
    proxies = ips[:]
    for rq_id, rq_data in data.items():
        proxy = proxies.pop(0)
        proxies.append(proxy)
        if not separated_data.get(proxy):
            separated_data[proxy] = {}
        separated_data[proxy][rq_id] = rq_data
    loaders = [OzDataLoader(proxy, src_data) for proxy, src_data in separated_data.items()]
    for ld in loaders:
        ld.start()
    for ld in loaders:
        ld.join()


def get_wb_goods():
    # oz_proxy_data_loader()
    # ows_get_wb_pages()
    # ows_get_oz_pages()
    collect_json_to_xls()
