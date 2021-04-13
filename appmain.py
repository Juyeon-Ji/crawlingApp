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
from common.log import make_logger
import pickle

def main():
    logger = make_logger()

    logger.info('Crawl Test')

    # driver = Selenium().driver

    ConfigManager()
    DatabaseManager()

    # pickle.dumps(DatabaseManager())
    # 카테고리 파싱 주석
    CategoryCrawl().run()

    # ProductCrawl()

    logger.info('Crawl Test End')

    # driver.quit()


if __name__ == '__main__':
    main()
