import json
from bs4 import BeautifulSoup


def get_price(src, platform):
    soup = BeautifulSoup(src, 'lxml')
    match platform:
        case 'baucenter':
            span = soup.find('span', class_='price-block_price')
            if not span:
                return
            price = float(span.text.strip().split('.–')[0].replace(' ', ''))
        case 'dns':
            pre = json.loads(soup.find('pre').text)
            price = float(pre['data']['offers']['price'])
        case 'maxidom':
            no_found_list = list(soup.find_all('h3'))
            if no_found_list:
                for el in no_found_list:
                    if 'К сожалению, по Вашему запросу ничего не найдено' in el.text:
                        return 'по Вашему запросу ничего не найдено'
            try:
                goods_list = soup.find('section', class_='items-list').find_all('article')
                if len(goods_list) == 1:
                    price_block = goods_list[0].find('span', class_='price-list')
                    price = float(price_block.span['data-repid_price'])
                else:
                    price = 'Неоднозначная идентификация'
            except AttributeError:
                price = soup.find('div', class_='price-big')['data-repid_price']
        case 'megastroy':
            price = float(soup.find('div', class_='price').b.text.replace(' ', ''))
        case 'vprok':
            no_found = soup.find('div', class_='xf-empty-search__message')
            if no_found:
                return 'по Вашему запросу ничего не найдено'
            price = float(soup.find('title').text.split('по цене ')[1].split(' руб.')[0])
        case 'petrovich':
            price_details = soup.find('div', class_='price-details')
            price = float(price_details.find_all('p')[1].text.split('₽')[0].replace(' ', ''))
        case 'ststroitel':
            price_value = soup.find('span', class_='price_value').text.split()
            price = float(''.join(price_value))
        case _:
            price = None
    return price


def get_data_from_loaded_page(src, merch_id, platform):
    try:
        price = get_price(src, platform)
    except Exception as ex:
        print(platform, merch_id, '*' * 30, ex)
        price = 'ERROR'
    return price
