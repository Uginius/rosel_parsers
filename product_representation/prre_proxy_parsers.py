from random import randint
from threading import Thread
from bs4 import BeautifulSoup
from logging_config import set_logging
from vpn.crome2 import Chrome2

log = set_logging('pre_proxy', write_errors=True)


def get_seller(seller):
    if 'продавец' in seller:
        return seller.split('продавец ')[1]
    if seller == 'За час курьером Ozon Express':
        return 'Ozon'
    return None


def get_oz_elements(html_product):
    divs = html_product.find_all('div', recursive=False)
    try:
        link = divs[1].find('a', class_='tile-hover-target')
    except IndexError:
        return None
    if not link:
        card = divs[0]
        link = card.find('a', class_='tile-hover-target')
        seller_div = card.find_all('div', recursive=False)[-1].find_all('div', recursive=False)[-1]
        merch_seller = get_seller(seller_div.find_all(recursive=False)[-1].text)
    else:
        merch_seller = get_seller(divs[2].find_all('div', recursive=False)[-1].find_all('span')[3].text)
    merch_name = link.text.strip()
    merch_url = 'https://www.ozon.ru' + link['href'].split('/?')[0]
    merch_id = merch_url.split('-')[-1]
    if 'http' in merch_id:
        merch_id = merch_id.split('/')[-1]
    return {'brand': merch_seller, 'shop_id': merch_id, 'name': merch_name, 'url': merch_url}


class ProxyGetterOz(Thread):

    def __init__(self, proxy, src, ll, log):
        super().__init__()
        self.proxy = proxy
        self.src = src
        self.total_len = ll
        self.log = log
        self.raw_data = None
        self.clean_data = None
        self.all_data = {}

    def run(self) -> None:
        browser = Chrome2(sandbox=True, proxy_passless=self.proxy)
        for rq_id, query in self.src.items():
            self.get_data_from_browser(rq_id=rq_id, query=query, browser=browser)
            if not self.raw_data:
                continue
            self.parse_data(rq_id=rq_id, query=query)
            # time.sleep(0.1)

    def get_data_from_browser(self, rq_id, query, browser):
        try:
            browser.get(f'https://www.ozon.ru/search/?text={query}', wait_time=randint(4, 9))
            soup = BeautifulSoup(browser.page_source(), 'lxml')
        except Exception as e:
            self.log.error(f'[oz] error getting data from browser, id: {rq_id}/{query}, {e}')
            soup = None
        if soup:
            try:
                product_class = soup.find('div', class_='widget-search-result-container').div.div['class']
                self.raw_data = soup.find_all('div', class_=product_class)
            except Exception as e:
                self.log.error(f'[oz] product class error, id: {rq_id}/{query}, {e}')
                self.raw_data = None

    def parse_data(self, rq_id, query):
        try:
            self.clean_data, data = None, {}
            for order, html_product in enumerate(self.raw_data, 1):
                merch = get_oz_elements(html_product)
                if not merch:
                    break
                data[order] = merch
            self.clean_data = data
            q_products = len(self.clean_data)
            if q_products == 4:
                raise Exception('Only 4 items found')
            self.all_data[rq_id] = self.clean_data
            self.log.info(f'oz, found {q_products:>3}, {self.proxy:>20}, {rq_id}/{self.total_len}:{query}')
        except Exception as e:
            self.log.error(f'[oz] parsing data error, id: {rq_id}/{query}, {e}')
