"""
use module
import os
"""
import logging

from crawl.categorycrawl import CategoryCrawl  # pylint: disable
from crawl.productcrawl import ProductCrawl
from common.database.dbmanager import DatabaseManager
from common.config.configmanager import ConfigManager
from common.driver.seleniumdriver import Selenium


def close(driver):
    """ Selenium Driver 를 닫는다.
        :return None
    """
    if driver is not None:
        driver.close()

        driver.quit()


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

    ConfigManager()
    DatabaseManager()

    # 카테고리 파싱 주석
    CategoryCrawl().parse()

    ProductCrawl()

    logger.info('Crawl Test End')
    close(driver)


if __name__ == '__main__':
    main()
