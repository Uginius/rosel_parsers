import time
import undetected_chromedriver as uc
from config import undetected_chromedriver_ver
from logging_config import set_logging

selenium_arguments = [
    '--no-first-run', '--no-service-autorun', '--password-store=basic',
    '--headless', '--no-sandbox']
log = set_logging('browser')


class Chrome2:
    def __init__(self, sandbox=False, timeout=30):
        self.options = uc.ChromeOptions()
        sa = selenium_arguments if sandbox is False else selenium_arguments[:-2]
        for sel_arg in sa:
            self.options.add_argument(sel_arg)
        self.browser = None
        self.timeout = timeout
        self.set_browser()

    def set_browser(self):
        self.browser = uc.Chrome(options=self.options, version_main=undetected_chromedriver_ver)
        self.browser.set_page_load_timeout(self.timeout)
        self.browser.maximize_window()

    def get(self, url, wait_time=3, trs=3):
        try:
            self.browser.get(url)
        except Exception as ex:
            trs = trs - 1 if trs > 0 else 0
            log.error(ex)
            if trs:
                log.info(f'*** attempts left: {trs}, try to get {url} again')
                self.get(url, wait_time=3, trs=trs)
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

    def scroll_up(self, wait_time=0.5):
        self.browser.execute_script(f"window.scrollTo(0, 0);")
        time.sleep(wait_time)

    def close(self):
        try:
            self.browser.close()
            self.browser.quit()
        except Exception as e:
            log.error(f'Browser error, {e}')


if __name__ == '__main__':
    browser = Chrome2(sandbox=True)
    browser.get('https://nowsecure.nl')
    time.sleep(5)
    browser.close()
