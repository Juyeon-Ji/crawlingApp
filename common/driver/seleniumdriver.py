import logging
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from common.util import Singleton


class Selenium(object, metaclass=Singleton):
    driver: WebDriver = None

    def __init__(self):
        logging.info('Selenium Driver init')
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")

        _CHROMEDRIVER_PATH = 'resource/chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=_CHROMEDRIVER_PATH, chrome_options=chrome_options)

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def quit(self):
        if self.driver is not None:
            self.quit()
