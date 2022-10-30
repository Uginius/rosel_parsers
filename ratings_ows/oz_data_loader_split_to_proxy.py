from math import ceil
from threading import Thread
from logging_config import set_logging
from utilites import ChromeBrowser
from vpn.sequre import ips

log = set_logging('ows')


class OzLinksGetter(Thread):
    instances_count = 0

    def __init__(self, ip, src_scope):
        super().__init__()
        OzLinksGetter.instances_count += 1
        self.instance_order = OzLinksGetter.instances_count
        self.src_scope = src_scope
        self.goods = {}
        ip_log_pass = {'https': f'http://{login}:{password}@{ip}'} if ip else None
        proxies = {'proxy': ip_log_pass}
        self.browser = ChromeBrowser(proxy=proxies) if ip else ChromeBrowser()

    def run(self) -> None:
        print(self.instance_order)


def split_scopes(data):
    q_ips, q_all = len(ips), len(data)
    q_scope = ceil(q_all / q_ips)
    scopes = {}
    ip = 0
    for order, el in enumerate(data.items()):
        if order % q_scope == 0:
            ip = ips.pop()
        merch = {el[0]: el[1]}
        if scopes.get(ip):
            scopes[ip].update(merch)
        else:
            scopes[ip] = merch
    return scopes


def get_oz_data_xl_src(data):
    getters = [OzLinksGetter(ip, scope) for ip, scope in split_scopes(data).items()]
    for getter in getters:
        getter.start()
    for getter in getters:
        if getter.is_alive():
            getter.join()
