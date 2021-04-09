import logging
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from common.util import Singleton


class Selenium(object, metaclass=Singleton):
    driver: WebDriver = None

    def __init__(self):
        logging.info('Selenium Driver init')
        _user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
            (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("user-agent=" + _user_agent)
        # chrome_options.add_argument("--disable-gpu")

        _CHROMEDRIVER_PATH = 'resource/chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=_CHROMEDRIVER_PATH, chrome_options=chrome_options)

    def close(self):
        if self.driver is not None:
            self.driver.close()

    def quit(self):
        if self.driver is not None:
            self.driver.close()
            self.quit()

    def find_element(self, by: By, element: WebElement, value: str):
        _element: WebElement = None
        try:
            _element = element.find_element(by, value)
        except Exception as e:
            _element = None
            return _element

        return _element
