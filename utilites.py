from datetime import datetime
import os
import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config import selenium_arguments, browser_path
from openpyxl import load_workbook
from config import date_template, dir_template, req_headers


def time_track(func):
    def surrogate(*args, **kwargs):
        started_at = time.time()
        result = func(*args, **kwargs)
        ended_at = time.time()
        elapsed = round(ended_at - started_at, 3)
        minutes = round(elapsed / 60, 2)
        print(f'Функция работала {elapsed} секунд(ы), или {minutes} минут\n')
        return result

    return surrogate


def check_dir(folder):
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
    except Exception as ex:
        print(ex)


def get_last_dir(folder):
    dates_dirs = [datetime.strptime(el, date_template) for el in os.listdir(folder) if re.findall(dir_template, el)]
    return sorted(dates_dirs)[-1].strftime(date_template)


def id_url_from_table(xls_filename, page):
    workbook = load_workbook(xls_filename)
    ws = workbook[page]
    stock = {}
    for order, row in enumerate(ws, 1):
        if order < 2:
            continue
        stock[order] = row[0].value
    return stock


def request_get_data(url, retry=3, timeout=20):
    try:
        response = requests.get(url=url, headers=req_headers, timeout=timeout)
    except Exception as ex:
        time.sleep(5)
        if retry:
            print(f'[INFO] retry={retry} =>', url)
            response = request_get_data(url=url, retry=retry - 1, timeout=timeout + 10)
        else:
            response = None
            print('Connection error', ex)
    return response


class ChromeBrowser:
    def __init__(self):
        options = webdriver.ChromeOptions()
        for sel_arg in selenium_arguments:
            options.add_argument(sel_arg)
        self.browser = webdriver.Chrome(service=Service(executable_path=browser_path), options=options)

    def get(self, url, wait_time=3):
        self.browser.get(url)
        time.sleep(wait_time)
        return self.browser.page_source

    def page_source(self):
        return self.browser.page_source

    def scroll_down(self, wait_time=0.5):
        last_height = self.browser.execute_script("return document.body.scrollHeight")
        self.browser.execute_script(f"window.scrollTo(0, {last_height});")
        time.sleep(wait_time)
        while True:
            self.browser.execute_script(f"window.scrollTo(0, document.body.scrollHeight);")
            new_height = self.browser.execute_script("return document.body.scrollHeight")
            time.sleep(wait_time)
            if new_height == last_height:
                break
            last_height = new_height
