"""
use module
import os
"""

from crawl.categorycrawl import CategoryCrawl  # pylint: disable
from crawl.productcrawl import ProductCrawl
from common.database.dbmanager import DatabaseManager
from common.config.configmanager import ConfigManager
from common.driver.seleniumdriver import Selenium
from common.log import make_logger
import pandas
from openpyxl import Workbook



def main():
    logger = make_logger()

    logger.info('Crawl Test')

    # driver = Selenium().driver

    ConfigManager()
    db = DatabaseManager()

    # 카테고리 파싱 주석
    # CategoryCrawl().parse()

    ProductCrawl().parse()

    logger.info('Crawl Test End')
    # driver.quit()


if __name__ == '__main__':
    main()
