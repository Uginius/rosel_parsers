from raitings_ows.ows_collect_jsondata_to_xlsx import convert_jsondata_to_xls
from raitings_ows.ows_oz_get_pages import OzJsonBrandsGetter
from raitings_ows.ows_wb_get_pages import WbJsonBrandsGetter
from utilites import time_track


@time_track
def ows_get_wb_pages():
    wb_getter = WbJsonBrandsGetter()
    wb_getter.run()


@time_track
def ows_get_oz_pages():
    oz_getter = OzJsonBrandsGetter()
    oz_getter.run()


@time_track
def collect_json_to_xls():
    convert_jsondata_to_xls()


def get_wb_goods():
    ows_get_wb_pages()
    ows_get_oz_pages()
    collect_json_to_xls()
