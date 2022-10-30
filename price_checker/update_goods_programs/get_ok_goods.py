from bs4 import BeautifulSoup
from config import today
from logging_config import set_logging
from price_checker.checker_utilites import update_goods_folder
from ratings_trade_platforms.product import Product
from utilites import write_json
from vpn.crome2 import Chrome2

srh = 'https://www.okeydostavka.ru/webapp/wcs/stores/servlet/SearchDisplay?categoryId=&storeId=10151&searchTerm='
links = [srh + 'фотон', srh + 'контакт', srh + 'рекорд', srh + 'safeline', ]
shop = 'ok'
log_ok = set_logging(f'price_{shop}')


def get_goods(html_list):
    products = {}
    for prod in html_list:
        cp = Product()
        link = prod.a
        cp.name = link.text.strip()
        cp.url = 'https://www.okeydostavka.ru' + prod.a['href']
        cp.shop_id = int(prod['data-catentry-id'])
        price_box = prod.find('div', class_='product-price')
        price_label = price_box.find('span', class_='price label label-red')
        if not price_label:
            price_label = price_box.find('span', class_='price label')
        price = price_label.text.split('₽')[0].replace(',', '.').split()
        cp.price = float(''.join(price))
        products.update(cp.json_items())
    return products


def start_getting_ok_products():
    goods = {}
    browser = Chrome2(sandbox=True)
    for url in links:
        log_ok(f'*** opening {url}')
        browser.get(url)
        soup = BeautifulSoup(browser.page_source(), 'lxml')
        products = get_goods(soup.find_all('div', class_='product ok-theme'))
        log_ok(f'*** collected {len(products)} items')
        goods.update(products)
    write_json(f'{update_goods_folder}data_{shop}_{today}.json', goods)
