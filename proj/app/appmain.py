import os
import sys
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

baseprojectpath = os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            )
baseprojectpathexists = False
for syspath in sys.path:
    if baseprojectpath == syspath :
        baseprojectpathexists = True
        break

if not baseprojectpathexists :
    sys.path.append(baseprojectpath)

from proj.app.crawl.categorycrawl import CategoryCrawl
from proj.app.crawl.productcrawl import ProductCrawl
from proj.common.database.dbmanager import DatabaseManager
from proj.common.config.configmanager import ConfigManager
from proj.common.driver.seleniumdriver import Selenium


def close(driver):
    if driver is not None:
        driver.close()


def make_logger(name=None):
    # 1 logger instance를 만든다.
    logger = logging.getLogger(name)

    # 2 logger의 level을 가장 낮은 수준인 DEBUG로 설정해둔다.
    logger.setLevel(logging.INFO)

    # 3 formatter 지정
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 4 handler instance 생성
    console = logging.StreamHandler()
    file_handler = logging.FileHandler(filename="test.log")

    # 5 handler 별로 다른 level 설정
    console.setLevel(logging.INFO)
    file_handler.setLevel(logging.DEBUG)

    # 6 handler 출력 format 지정
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 7 logger에 handler 추가
    logger.addHandler(console)
    logger.addHandler(file_handler)

    return logger

def main():
    logger = make_logger()

    logger.info('Crawl Test')

    driver = Selenium().driver

    configmanager = ConfigManager()
    databasemanager = DatabaseManager()

    # CHROMEDRIVER_PATH = '../resource/chromedriver.exe'
    # # CHROMEDRIVER_PATH = 'D:/_1.project/WEBuilder/python_project/git_crawling/crawlingApp/proj/resource/chromedriver.exe'
    #
    # chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-gpu")
    # # chrome_options.add_argument( f"--window-size={ WINDOW_SIZE }" )

    # driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)

    # categorycrawl = CategoryCrawl()
    #
    # categorycrawl.parse()
    #
    # category = ProductCrawl()

    logger.info('Crawl Test End')
    close(driver)

if __name__ == '__main__':
    main()