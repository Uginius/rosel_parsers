import datetime
import sys

computer = sys.platform

ua_win = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
ua_mac = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) ' \
         'Chrome/105.0.0.0 Safari/537.36'
ua_computers = {'linux': None, 'darwin': ua_mac, 'win32': ua_win}
driver_path = {'linux': None, 'darwin': 'drivers/chromedriver', 'win32': 'drivers/chromedriver.exe'}
browser_path = driver_path[computer]
ua = ua_computers[computer]
selenium_arguments = [f'user-agent={ua}', '--disable-blink-features=AutomationControlled', '--headless', '--no-sandbox']
req_headers = {
    'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': ua}

dir_template, date_template = r'202\d-\d{2}-\d{2}', '%Y-%m-%d'
today = datetime.datetime.now().strftime(date_template)

shops = ['akson', 'baucenter', 'dns', 'maxidom', 'sdvor', 'votonia']
