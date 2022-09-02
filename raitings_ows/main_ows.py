import os

from utilites import ChromeBrowser

folder = 'raitings_ows/all_rosel_htmls'


def load_data():
    browser = ChromeBrowser()
    for page in range(1, 5):
        print(page)
        # url = f'https://www.wildberries.ru/seller/30766?sort=popular&page={page}'
        url = f'https://catalog.wb.ru/sellers/catalog?appType=1&couponsGeo=12,7,3,6,5,18,21&curr=rub&dest=-1216601,-337422,-1114902,-1198055&emp=0&lang=ru&locale=ru&page={page}&pricemarginCoeff=1.0&reg=0&regions=68,64,83,4,38,80,33,70,82,86,30,69,22,66,31,40,1,48&sort=popular&spp=0&supplier=30766'
        browser.get(url, wait_time=5)
        filename = f'{folder}/json_wb_page_{page:02}.html'
        with open(filename, 'w', encoding='utf8') as write_file:
            write_file.write(browser.page_source())


def parse_data():
    files = os.listdir(folder)
    print(files)


def get_wb_goods():
    load_data()
    # parse_data()


