import logging
from selenium import webdriver

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            pass
            # 매번 __init__ 호출하고 싶으면 아래 주석 제거
            # cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Selenium(object, metaclass=Singleton):
    driver: WebDriver = None

    def __init__(self):
        logging.info('Selenium Driver init')
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")

        _CHROMEDRIVER_PATH = '../resource/chromedriver.exe'
        self.driver = webdriver.Chrome(executable_path=_CHROMEDRIVER_PATH, chrome_options=chrome_options)

