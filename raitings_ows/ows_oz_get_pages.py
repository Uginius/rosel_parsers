import time
from bs4 import BeautifulSoup
from config import today
from logging_config import set_logging
from ratings_trade_platforms.product import Product
from utilites import ChromeBrowser, check_dir, write_json

log = set_logging('ows_oz')


def set_urls():
    urls = []
    for page in range(1, 13):
        url = f'https://www.ozon.ru/search/?from_global=true&page={page}&seller=6793'
        urls.append(url)
    return urls


def collect_data(soup):
    goods_html = soup.find('div', class_='widget-search-result-container').div
    goods = {}
    for merch in goods_html.find_all('div', recursive=False):
        if not merch.text:
            continue
        data_merch = merch.find_all(recursive=False)[1]
        merch_divs = data_merch.find_all('div', recursive=False)
        cp = Product()
        local_a = data_merch.a
        cp.shop_id = int(local_a['href'].split('/?')[0].split('-')[-1])
        cp.name = local_a.text.strip()
        cp.url = 'https://www.ozon.ru' + local_a['href'].split('?')[0]
        try:
            price = merch_divs[1].text.split(' ₽')[0]
            cp.price = float(''.join(price.split()))
        except Exception as ex:
            log.error(f'Cant get price #{cp.shop_id}, {cp.name}, {cp.url}, {ex}')
            cp.price = None
        rate_box = merch_divs[3]
        if 'продавец' in rate_box.text:
            rate_box = merch_divs[2]
        try:
            rtb = rate_box.div.div.find_all('div', recursive=False)[1]
            rating = float(rtb['style'].split(':')[1][:-2])
            cp.rating = round((5 * rating) / 100, 2)
            cp.feedbacks = int(rate_box.a.text.split()[0])
        except Exception as ex:
            log.error(f'Cant get rating #{cp.shop_id}, {cp.name}, {cp.url}, {ex}')
            cp.rating, cp.feedbacks = None, None
        pass
        # local_a = merch.find_all('a')[1]
        # cp.shop_id = int(local_a['href'].split('/?')[0].split('-')[-1])
        # cp.name = local_a.text.strip()
        # cp.url = 'https://www.ozon.ru' + local_a['href'].split('?')[0]
        # try:
        #     rating = float(merch.find('div', class_='ui-da3')['style'].split(':')[1][:-2])
        #     cp.rating = round((5 * rating) / 100, 2)
        #     cp.feedbacks = int(merch.find('div', class_='rk3 yd2').a.text.split()[0])
        # except Exception as ex:
        #     log.error(f'Cant get rating #{cp.shop_id}, {cp.name}, {cp.url}, {ex}')
        #     cp.rating, cp.feedbacks = None, None
        # try:
        #     cp.price = merch.find('div', class_='ui-o4').text.split(' ₽')[0]
        # except Exception as ex:
        #     log.error(f'Cant get price #{cp.shop_id}, {cp.name}, {cp.url}, {ex}')
        #     cp.price = None
        goods.update(cp.json_items())
    return goods


class OzJsonBrandsGetter:
    def __init__(self):
        self.brand_links = set_urls()
        self.goods = {}

    def run(self):
        self.get_pages()
        self.save_json()

    def get_pages(self):
        for order, url in enumerate(self.brand_links, 1):
            log.info(f'{order:>2}: Connect to {url}')
            self.get_and_parse_page(url)

    def get_and_parse_page(self, url):
        browser = ChromeBrowser(sandbox=True)
        browser.get(url)
        time.sleep(3)
        browser.scroll_down()
        time.sleep(1)
        data = collect_data(BeautifulSoup(browser.page_source(), 'lxml'))
        self.goods.update(data)
        browser.close()
        time.sleep(1)
        log.info(f'Collected {len(data)} items')

    def save_json(self):
        folder = f'raitings_ows/json_files'
        check_dir(folder)
        json_filename = f'{folder}/oz_{today}.json'
        write_json(json_filename, self.goods)
        log.info(f'file {json_filename} saved')
