from bs4 import BeautifulSoup

from config import today
from price_checker.prc_update_products import update_goods_folder
from ratings_trade_platforms.product import Product
from utilites import write_json
from vpn.crome2 import Chrome2

url = 'https://online.globus.ru/catalog/avto-dacha-remont/filter/brands-is-545670-or-245825-or-230840-or-280153/apply/'


def get_goods(html_list):
    products = {}
    for prod in html_list:
        cp = Product()
        link = prod.a
        cp.name = link.span.text.strip()
        cp.url = 'https://online.globus.ru' + prod.a['href']
        cp.shop_id = cp.url.split('/')[-2]
        price_box = prod.find('span', class_='catalog-section__item-info')
        rub = price_box.find('span', class_='item-price__rub').text.split()
        kop = price_box.find('span', class_='item-price__kop').text.strip()
        cp.price = float(f'{"".join(rub)}.{kop}')
        products.update(cp.json_items())
    return products


def start_getting_globus_products():
    goods = {}
    browser = Chrome2()
    print(f'*** opening {url}')
    browser.get(url)
    soup = BeautifulSoup(browser.page_source(), 'lxml')
    products = get_goods(soup.find_all('div', class_='catalog-section__item catalog-section__item--main'))
    print(f'*** collected {len(products)} items')
    goods.update(products)
    write_json(f'{update_goods_folder}data_globus_{today}.json', goods)

