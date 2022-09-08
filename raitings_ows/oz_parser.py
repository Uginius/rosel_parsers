import os
import random
from bs4 import BeautifulSoup
from openpyxl import Workbook
from config import today
from utilites import check_dir, ChromeBrowser

folder = f'raitings_ows/htmls_oz/{today}'


def get_oz_pages():
    check_dir(folder)
    browser = ChromeBrowser()
    for page in range(1, 14):
        url = f'https://www.ozon.ru/search/?from_global=true&page={page}&seller=6793'
        print(url)
        wait_time = random.randint(3, 8)
        browser.get(url, wait_time=wait_time)
        filename = f'{folder}/oz_page_{page:02}.html'
        with open(filename, 'w', encoding='utf8') as write_file:
            write_file.write(browser.page_source())


def collect_data(soup):
    goods_html = soup.find('div', class_='widget-search-result-container').div
    goods = {}
    for order, merch in enumerate(goods_html.find_all('div', recursive=False), 0):
        if not merch.text:
            continue
        local_a = merch.find_all('a')[1]
        shop_id = int(local_a['href'].split('/?')[0].split('-')[-1][:-1])
        try:
            rating = float(merch.find('div', class_='ui-da0')['style'].split(':')[1][:-2])
            rating = round((5 * rating) / 100, 2)
            feedbacks = int(merch.find('div', class_='w9j dt2').a.text.split()[0])
        except Exception as ex:
            print(f'------- product #{order}', ex)
            rating, feedbacks = None, None
        price = merch.find('div', class_='ui-n9').text.split(' ₽')
        goods[shop_id] = {
            'name': local_a.text.strip(),
            'brand': None,
            'old_price': price[1],
            'price': price[0],
            'rating': rating,
            'feedbacks': feedbacks,
            'url': 'https://www.ozon.ru' + local_a['href'].split('?')[0]
        }
    return goods


def parse_oz_files():
    goods = {}
    for filename in sorted(os.listdir(folder)):
        with open(f'{folder}/{filename}', 'r', encoding='utf8') as read_file:
            print(filename)
            data = collect_data(BeautifulSoup(read_file.read(), 'lxml'))
            goods.update(data)
    return goods


def make_xls_file(data):
    workbook = Workbook()
    ws = workbook.active
    title = ['shop_id', 'name', 'brand', 'url', 'price', 'rating', 'feedbacks']
    ws.append(title)
    for shop_id, p in data.items():
        prod = [shop_id, p['name'], p['brand'], p['url'], p['price'], p['rating'], p['feedbacks']]
        ws.append(prod)
    result_dir = 'xls_results'
    check_dir(result_dir)
    workbook.save(f"{result_dir}/oz_data_{today}.xlsx")


def oz_data_getter():
    # get_oz_pages()
    data = parse_oz_files()
    make_xls_file(data)
