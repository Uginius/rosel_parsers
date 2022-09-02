import datetime
import sys

ua = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'
driver_path = {'linux': None, 'darwin': 'drivers/chromedriver', 'win32': 'drivers/chromedriver.exe'}
browser_path = driver_path[sys.platform]
selenium_arguments = [f'user-agent={ua}', '--disable-blink-features=AutomationControlled', '--headless', '--no-sandbox']
req_headers = {
    'accept': '*/*', 'accept-encoding': 'gzip, deflate, br', 'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'user-agent': ua}

dir_template, date_template = r'202\d-\d{2}-\d{2}', '%Y-%m-%d'
today = datetime.datetime.now().strftime(date_template)
