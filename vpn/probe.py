from random import choice
import requests
from bs4 import BeautifulSoup
from config import req_headers
from vpn.sequre import login, password, ips


def get_location(url):
    proxy_dict = {'https': f'http://{login}:{password}@{choice(ips)}'}
    rq = requests.get(url, headers=req_headers, proxies=proxy_dict)
    soup = BeautifulSoup(rq.text, 'lxml')
    ip_adr = soup.find('div', id='d_clip_button').text.strip()
    location = soup.find('div', class_='value value-country').text.strip()
    print(f'IP: {ip_adr}, Location: {location}')


if __name__ == '__main__':
    get_location('https://2ip.ru/')
