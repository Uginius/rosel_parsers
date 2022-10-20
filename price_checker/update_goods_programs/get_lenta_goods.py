from bs4 import BeautifulSoup

from config import today
from price_checker.prc_update_products import update_goods_folder
from ratings_trade_platforms.product import Product
from utilites import ChromeBrowser, write_json

lenta_urls = [
    'https://lenta.com/search/?searchText=%D0%9A%D0%BE%D0%BD%D1%82%D0%B0%D0%BA%D1%82',
    'https://lenta.com/search/?searchText=%D0%A4%D0%BE%D1%82%D0%BE%D0%BD&page=1',
    'https://lenta.com/search/?searchText=%D0%A4%D0%BE%D1%82%D0%BE%D0%BD&page=2',
    'https://lenta.com/search/?searchText=%D0%A4%D0%BE%D1%82%D0%BE%D0%BD&page=3',
    'https://lenta.com/search/?searchText=Safeline',
    'https://lenta.com/search/?searchText=%D0%A0%D0%B5%D0%BA%D0%BE%D1%80%D0%B4',
]


def get_goods(html_list):
    products = {}
    for prod in html_list:
        cp = Product()
        cp.name = prod.find('div', class_='sku-card-small-header__title').text.strip()
        cp.url = 'https://lenta.com' + prod.a['href']
        cp.shop_id = cp.url.split('-')[-1][:-1]
        cp.rating = float(prod.find('span', class_='sku-card-small-header__rating-text').text)
        cp.feedbacks = int(prod.find('span', class_='sku-card-small-header__comments-text').text)
        try:
            cp.price = float(prod.find('span', class_='price-label__integer').text)
        except Exception as ex:
            cp.price = None
            cp.status = prod.find('div', class_='sku-card-small__not-available-notice').text.strip()
            print(f'Cant get price, {ex}')
        products.update(cp.json_items())
    return products


def start_getting_lenta_products():
    goods = {}
    browser = ChromeBrowser()
    for url in lenta_urls:
        print(f'*** opening {url}')
        browser.get(url)
        soup = BeautifulSoup(browser.page_source(), 'lxml')
        products = get_goods(soup.find_all('div', class_='sku-card-small-container'))
        print(f'*** collected {len(products)} items')
        goods.update(products)
    write_json(f'{update_goods_folder}data_lenta_{today}.json', goods)


if __name__ == '__main__':
    start_getting_lenta_products()
