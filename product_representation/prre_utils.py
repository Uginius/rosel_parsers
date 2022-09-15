import os
import re
from datetime import datetime
from config import dir_template, date_template, month_template
from product_representation.src.prre_goals import goals_and_terms


def get_last_month(folder):
    dates_dirs = [datetime.strptime(el, month_template) for el in os.listdir(folder)]
    return sorted(dates_dirs)[-1].strftime(month_template)


def last_month_json_files(shop):
    folder = "product_representation/json_files"
    folder = os.path.join(folder, get_last_month(folder))
    jsf = {}
    for filename in os.listdir(folder):
        find_date = re.findall(dir_template, filename)
        is_platform = shop in filename
        if find_date and is_platform:
            jsf[datetime.strptime(find_date[0], date_template)] = filename
    dates = sorted(list(jsf.keys()))
    last = dates[-1]
    last_month_files = {d: f'{folder}/{jsf[d]}' for d in dates if d.year == last.year and d.month == last.month}
    return last_month_files


def get_first_rqs(platform):
    last_cat = ''
    first_requests = {}
    for rq, terms in goals_and_terms[platform].items():
        category = terms['category']
        if category != last_cat:
            first_requests[rq] = category
            last_cat = category
    return first_requests
