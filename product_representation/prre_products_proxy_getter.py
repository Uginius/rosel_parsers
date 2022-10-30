import time
from threading import Thread
from config import cur_month, today
from logging_config import set_logging
from product_representation.prre_proxy_parsers import ProxyGetterOz
from product_representation.src.prre_goals import goals_and_terms
from utilites import write_json, check_dir
from vpn.sequre import ips

logs_name = 'pre_proxy'
log = set_logging(logs_name)
gts = {'oz': ProxyGetterOz}


class PrRePageProxyGetter(Thread):
    def __init__(self, shop):
        super().__init__()
        self.platform = shop
        self.goals = goals_and_terms[shop]
        self.proxies_requests = {}
        self.result_data = {}
        self.json_folder = check_dir(f'product_representation/json_files/{cur_month}')
        self.i_see_error = True
        self.error_ids = []

    def run(self):
        log.info(f'★★★ Product representation on {self.platform} started ★★★')
        self.get_pages()
        while self.i_see_error:
            self.check_errors()
        self.save_json()

    def get_pages(self, src_data=None, msg='start to get pages ******'):
        log.info(f'{self.platform} - {msg}')
        if not src_data:
            src_data = self.goals
        self.split_for_proxy(src_data)
        ll = len(src_data)
        market = gts[self.platform]
        getters = [market(proxy, qq, ll, log) for proxy, qq in self.proxies_requests.items()]
        for getter in getters:
            getter.start()
        for getter in getters:
            getter.join()
            self.result_data.update(getter.all_data)

    def split_for_proxy(self, src_data):
        self.proxies_requests = {}
        result = self.proxies_requests
        proxies = ips[:]
        for rq_id, rq_data in src_data.items():
            proxy = proxies.pop(0)
            proxies.append(proxy)
            if not result.get(proxy):
                result[proxy] = {}
            result[proxy][rq_id] = rq_data['request']

    def check_errors(self):
        log_filename = f'logs/{logs_name}_err.log'
        errors = self.error_ids
        with open(log_filename, 'r', encoding='utf8') as rf:
            for line in rf:
                if 'ERROR' in line:
                    platform = line.split('| [')[1].split(']')[0]
                    if platform != self.platform:
                        continue
                    rq_id = line.split('id: ')[1].split('/')[0]
                    errors.append(rq_id)
        if errors:
            with open(log_filename, 'w', encoding='utf8'):
                pass
            log.info(f'Found {len(errors)} errors on the [{self.platform}]')
            time.sleep(3)
            self.get_selected_rqs()
        else:
            self.i_see_error = False

    def get_selected_rqs(self):
        goal_to_rq = {}
        while self.error_ids:
            rq_id = self.error_ids.pop()
            goal_to_rq[rq_id] = self.goals[rq_id]
        self.get_pages(goal_to_rq, msg=f'Trying to get {len(goal_to_rq)} pages ******')

    def save_json(self):
        json_filename = f'{self.json_folder}/{self.platform}_{today}.json'
        write_json(json_filename, self.result_data)
        log.info(f'{json_filename} saved')


if __name__ == '__main__':
    oz_getter = PrRePageProxyGetter('oz')
    oz_getter.run()
