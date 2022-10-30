import json
import random
import time
import requests
from bs4 import BeautifulSoup

from logging_config import set_logging
from ratings_trade_platforms.product import Product
from ratings_trade_platforms.tp_config import brand_list
from utilites import ChromeBrowser

log = set_logging('pla_parsers')


def get_maxidom_rating(url):
    try:
        browser = ChromeBrowser()
        browser.get(url, wait_time=random.randint(1, 4))
        soup = BeautifulSoup(browser.page_source(), 'lxml')
        data = json.loads(soup.find('pre').text)['Stats']
        review_count = data['ReviewsTotalCount']
        rates_total_sum = data['RatesTotalSum']
        rating_value = round(rates_total_sum / review_count, 2) if review_count else None
    except Exception as ex:
        log.error(ex)
        rating_value, review_count = None, None
    return [rating_value, review_count]


def bau_goods_parser(html_product):
    cp = Product()
    tm = html_product['data-brand']
    if tm.upper() not in brand_list:
        return None
    cp.trade_mark = tm
    cp.shop_id = int(html_product['data-article'])
    cp.name = html_product['data-name']
    if 'Стул' in cp.name:
        return None
    link = html_product.find('a', attrs={'data-gtm-event': 'product_click'})['href']
    cp.url = f"https://baucenter.ru{link}"
    try:
        stock = html_product.find('div', class_='stock-list').p.text
        cp.status = ' '.join(stock.split())
    except AttributeError:
        cp.status = 'Отсутствуют в продаже'
    try:
        cp.price = float(html_product['data-price'])
    except AttributeError:
        cp.price = 'Нет данных'
    votes = html_product.find('div', class_='catalog_item_rating')
    if votes.text.strip():
        cp.feedbacks = int(votes.text.strip())
        percent = int(votes.find('div', class_='raiting-votes')['style'].split(':')[1][:-2])
        cp.rating = (percent * 5) / 100
    return cp


def sdvor_goods_parser(html_product):
    cp = Product()
    cp.shop_id = int(html_product.find('span', class_='code-value').text)
    link = html_product.find('a', class_='product-name')
    name = link.text.strip().split()
    cp.name = ' '.join(name)
    cp.url = 'https://www.sdvor.com' + link['href']
    try:
        price = html_product.find('div', class_='price').text.strip().split()[:-1]
        price = price.split('₽')[0] if '₽' in price else price
        cp.price = float(''.join(price))
    except AttributeError:
        cp.price = None
    if 'Фотон'.upper() in cp.name.upper():
        cp.trade_mark = 'ФОТОН'
    elif 'Изолента'.upper() in cp.name.upper():
        cp.trade_mark = 'SafeLine'
    try:
        status = html_product.find('span', class_='shops-text check-availability').text
        if status == 'Проверить наличие':
            cp.status = 'в наличии'
        else:
            cp.status = 'Нет данных'
    except Exception:
        cp.status = 'Нет в наличии'
    div_rating = html_product.find('div', class_='rating')
    if div_rating:
        url = f'https://www.sdvor.com/api/mneniya-pro/v1.3/ratings/Product/{cp.shop_id}'
        response = requests.get(url)
        time.sleep(1)
        json_resp = response.json()[0]
        cp.feedbacks = json_resp['TotalReviewsCount']
        cp.rating = json_resp['TotalScore']
    return cp


def dns_goods_parser(html_product):
    cp = Product()
    cp.shop_id = int(html_product['data-code'])
    cp.name = html_product.find('span').text
    cp.url = f"https://www.dns-shop.ru{html_product.find('a')['href']}"
    try:
        cp.status = html_product.find('div', class_='order-avail-wrap').text.strip()
        if cp.status == 'Товара нет в наличии':
            cp.status = 'Нет в наличии'
        if 'В наличии:' in cp.status or 'В магазинах:' in cp.status:
            cp.status = 'в наличии'
    except AttributeError:
        cp.status = 'Отсутствуют в продаже'
    try:
        price = html_product.find('div', class_='product-buy__price').text.split('₽')[0].split()
        cp.price = int(''.join(price))
    except AttributeError:
        cp.price = 'Продажи прекращены'
        return None
    if 'ФОТОН' in cp.name.upper():
        cp.trade_mark = 'ФОТОН'
    votes = html_product.find('a', class_='catalog-product__rating ui-link ui-link_black')
    cp.rating = votes['data-rating']
    cp.rating = float(cp.rating)
    cp.feedbacks = votes.text.strip()
    if cp.feedbacks == 'нет отзывов':
        cp.feedbacks = 0
    cp.feedbacks = int(cp.feedbacks)
    return cp


def akson_goods_parser(html_prod):
    cp = Product()
    cp.name = html_prod.find('a', class_='info-title text-body-regular text-color-headline').text
    not_rosel_brand, cp.trade_mark = check_brand_for_akson(cp.name.upper())
    if not_rosel_brand:
        return
    cp.shop_id = int(
        html_prod.find('div', class_='info-code mb-1 text-body-regular text-color-secondary').text.split()[1])
    cp.url = f"https://akson.ru{html_prod.find('a')['href']}"
    try:
        button_text = html_prod.find('button').text
        if button_text == 'В корзину':
            cp.status = 'в наличии'
    except AttributeError:
        cp.status = 'Отсутствуют в продаже'
    try:
        price = html_prod.find('span', class_='info-price__value text-header-l-bold').text.split()
        cp.price = float(''.join(price))
    except AttributeError:
        cp.price = 'Продажи прекращены'
    try:
        rate = html_prod.find('span', class_='rating')
        stars = rate.find('span', class_='stars__block stars__block_fill')['style']
        percent = int(stars.split(':')[1][:-2])
        cp.rating = (percent * 5) / 100
        cp.feedbacks = int(rate.text.split('(')[1].split(')')[0])
    except TypeError as ex:
        log.error(f'akson rating error, {ex}')
    return cp


def check_brand_for_akson(name):
    trade_mark = None
    brandlist = ['ФОТОН', 'РЕКОРД', 'КОНТАКТ', 'SafeLine']
    for brand in brandlist:
        if brand.upper() in name:
            trade_mark = brand
            break
    stop_words = ['Бетон', 'Планка', 'Профиль', 'Фотообои', 'Очаг', 'Разъем', 'Фоторамка', 'Портал', 'Секатор']
    for word in stop_words:
        no_our_brand = word.upper() in name
        if no_our_brand:
            return True, None
    return False, trade_mark


def maxidom_goods_parser(html_product):
    cp = Product()
    art_block = html_product.find_all('small', class_="sku")
    split_rosel_id = art_block[0].text.split()[1].replace('.', '')
    split_id = art_block[1].text.split()[-1]
    cp.shop_id = int(split_id)
    if '/' in split_rosel_id:
        split_rosel_id = split_rosel_id.split('/')[0]
    try:
        cp.rosel_id = int(split_rosel_id)
    except ValueError:
        cp.rosel_id = None
    cp.trade_mark = art_block[2].text.split(':')[1].strip()
    link = html_product.find(attrs={'itemprop': 'name'})
    cp.name = link.text
    cp.url = 'https://www.maxidom.ru' + link['href']
    cp.status = html_product.find('div', class_='item-controls').span.text.strip()
    cp.price = float(html_product.find('span', class_='price-list').text.split(',-')[0].strip().replace(' ', ''))
    maxi_url = f'https://www.maxidom.ru/ajax/mneniya_pro/getReviewsHtml.php?SKU_ID={cp.shop_id}'
    log.info(f'maxidom _____ opening {maxi_url}')
    cp.rating, cp.feedbacks = get_maxidom_rating(maxi_url)
    return cp


def get_votonia_rating(url):
    response = requests.get(url)
    time.sleep(random.randint(2, 5))
    try:
        soup = BeautifulSoup(response.text, 'lxml')
        tab_review = soup.find('div', id="tab-review").find('div', class_='row').div
        line = tab_review.find('div', class_='review_info_line')
        rating_value = float(line.b.text.strip().replace('"', ''))
        review_count = int(line.text.strip().split()[-2])
    except Exception as ex:
        log.error(f'Votonia rating error, {url}, {ex}')
        rating_value, review_count = None, None
    return [rating_value, review_count]


def votonia_goods_parser(html_product):
    cp = Product()
    cp.shop_id = html_product['data-id']
    link = html_product.find('a', class_='product_link')
    cp.name = link.text.strip()
    cp.url = 'https://www.votonia.ru' + link['href']
    cp.price = float(html_product['data-market'])
    cp.trade_mark = 'Фотон'
    cp.status = html_product.find('div', class_='reach_line').text.strip()
    cp.rating, cp.feedbacks = get_votonia_rating(cp.url)
    return cp


tp_parser = {'akson': akson_goods_parser, 'baucenter': bau_goods_parser, 'dns': dns_goods_parser,
             'maxidom': maxidom_goods_parser, 'sdvor': sdvor_goods_parser, 'votonia': votonia_goods_parser}
