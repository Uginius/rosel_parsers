from random import choice
import requests
from bs4 import BeautifulSoup
from config import req_headers
from vpn.crome2 import Chrome2
from vpn.sequre import ips


# def get_user_pass_location(url):
#     proxy_dict = {'https': f'http://{login}:{password}@{choice(ips)}'}
#     rq = requests.get(url, headers=req_headers, proxies=proxy_dict)
#     soup = BeautifulSoup(rq.text, 'lxml')
#     ip_adr = soup.find('div', id='d_clip_button').text.strip()
#     location = soup.find('div', class_='value value-country').text.strip()
#     print(f'IP: {ip_adr}, Location: {location}')


def get_fp_location(url, proxy):
    rq = requests.get(url, headers=req_headers, proxies=proxy)
    soup = BeautifulSoup(rq.text, 'lxml')
    ip_adr = soup.find('div', id='d_clip_button').text.strip()
    location = soup.find('div', class_='value value-country').text.strip()
    print(f'IP: {ip_adr}, Location: {location}')


def get_browser_location(url, proxy):
    browser = Chrome2(proxy_passless=proxy, sandbox=True)
    browser.get(url, wait_time=0)
    soup = BeautifulSoup(browser.page_source(), 'lxml')
    ip_adr = soup.find('div', id='d_clip_button').text.strip()
    location = soup.find('div', class_='value value-country').text.strip()
    print(f'IP: {ip_adr}, Location: {location}')


if __name__ == '__main__':
    url = 'https://2ip.ru/'
    # get_fp_location(url, {'https': proxy})
    get_browser_location(url, proxy=choice(ips))
