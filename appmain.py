"""
use module
import os
"""
import os
import sys
import logging

baseprojectpath = os.path.dirname(
    os.path.dirname(os.path.dirname(__file__))
)

BASE_PATH_EXISTS = False

for syspath in sys.path:
    if baseprojectpath == syspath:
        BASE_PATH_EXISTS = True
        break

if not BASE_PATH_EXISTS:
    sys.path.append(baseprojectpath)

from crawl.categorycrawl import CategoryCrawl  # pylint: disable
from crawl.productcrawl import ProductCrawl
from common.database import DatabaseManager
from common.config.configmanager import ConfigManager
from common.driver.seleniumdriver import Selenium


def close(driver):
    """ Selenium Driver 를 닫는다.
        :return None
    """
    if driver is not None:
        driver.close()


def make_logger(name=None):
    """ make Logger
        :return logger
    """
    # 1 logger instance를 만든다.
    logger = logging.getLogger(name)

    # 2 logger의 level을 가장 낮은 수준인 DEBUG로 설정해둔다.
    logger.setLevel(logging.INFO)

    # 3 formatter 지정
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # 4 handler instance 생성
    console = logging.StreamHandler()
    file_handler = logging.FileHandler(filename="proj/app/test.log")

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

    ConfigManager()
    DatabaseManager()

    CategoryCrawl().parse()

    ProductCrawl()

    logger.info('Crawl Test End')
    close(driver)


if __name__ == '__main__':
    main()