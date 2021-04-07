import re
import time
import logging
from operator import eq
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.remote.webelement import WebElement

from common.util import Utils
from common.driver.seleniumdriver import Selenium
from common.database.dbmanager import DatabaseManager
from common.config.configmanager import CrawlConfiguration, ConfigManager


def _join_path(token, source: str, value: str) -> str:
    return token.join([source, value])


class CategoryCrawl(object):
    URL = 'https://shopping.naver.com/'
    DELIMITER = 'cat_id='

    def __init__(self):
        # 크롬 selenium Driver - singleton
        self.driver = Selenium().driver
        # 크롤링 설정 정보 관리 - singleton
        self.crawl_config: CrawlConfiguration = ConfigManager().crawl_config
        # Database manager - 데이터 조회 및 저장을 여기서 합니다. - singleton
        self.database_manager = DatabaseManager()

    def _parse_cat_id(self, value: str) -> str:
        if value is not None:
            x = 0
            x = value.find(self.DELIMITER)
            if x != -1:
                x = x + len(self.DELIMITER) - 1
                return value[x + 1:len(value)]

    def _insert(self, cid, name, paths: str):
        """ Mongo Database Insert """
        _category_document = dict()

        _category_document['cid'] = cid
        _category_document['name'] = name
        _category_document['paths'] = paths

        return self.database_manager.insert_one_mongo('category', _category_document)

    def _is_exists(self, cid):
        """MongoDB에 cid 값을 조회하여 조건에 맞는 document가 있는지 확인"""
        _query = self.database_manager.find_query('cid', cid)
        return self.database_manager.count_document_exists(_query)

    def parse(self):
        self.driver.get(self.URL)

        try:
            for category in self.driver.find_elements_by_xpath('//*[@id="home_category_area"]/div[1]/ul/li'):
                time.sleep(1)
                self._parse_root(category)

        except Exception as e:
            logging.error(str(e))

    def _parse_root(self, category: WebElement):
        # Root 이름
        text: str = category.text
        root_name = text.replace('/', '-')

        logging.info('rootName : ' + root_name)

        for exclude_category in self.crawl_config.exclude_category:
            if eq(root_name, exclude_category):
                return None

        class_att = category.get_attribute('class')
        click_xpath = '//*[@id="home_{0}"]'.format(class_att)

        self.driver.implicitly_wait(5)
        # 먼저 클릭해봄.
        self.driver.find_element_by_xpath(click_xpath).send_keys(Keys.ENTER)
        # class_att 맞춰 내부 xPath 설정
        time.sleep(1)

        xpath_cate = '//*[@id="home_{0}_inner"]/div[1]'.format(class_att)

        # Root Category
        element: WebElement = None
        while 1:
            if element is not None:
                break
            else:
                # 클릭 이벤트가 정상적으로 안들어오면 계속 클릭하자..
                self.driver.find_element_by_xpath(click_xpath).send_keys(Keys.ENTER)
                self.driver.implicitly_wait(4)
                time.sleep(1)
                element = self.driver.find_element_by_xpath(xpath_cate)

        self._insert(None, root_name, None)
        # Root -> sub
        sub_category = element.find_elements(By.CLASS_NAME, 'co_col')

        self._parse_sub(sub_category, root_name)

    def _parse_sub(self, sub_category, root_name):
        sub_item: WebElement
        for sub_item in sub_category:
            time.sleep(1)
            # 중간 카테고리
            # href
            sub_href = sub_element.find_element_by_tag_name('a').get_attribute('href')
            # cid
            _cid = self._parse_cat_id(sub_href)

            if self._is_exists(_cid):
                time.sleep(1)
                continue

            sub_element: WebElement = sub_item.find_element_by_tag_name('strong')
            # name
            _name = sub_element.find_element_by_tag_name('a').text
            _name = re.sub("전체보기", "", _name)
            # paths
            _paths = Utils.join_path(token='#', source=root_name, value=_name)

            # cid, name, paths
            self._insert(_cid, _name, _paths)

            # 하위 카테고리 리스트
            child_items: [WebElement] = sub_item.find_elements(By.TAG_NAME, 'li')
            self._parse_child(child_items, _paths)

    def _parse_child(self, child_items, sub_paths):
        child_item: WebElement
        for child_item in child_items:
            time.sleep(1)
            # href
            _href = child_item.find_element_by_tag_name('a').get_attribute('href')
            # cid
            _cid = self._parse_cat_id(_href)
            if self._is_exists(_cid):
                time.sleep(1)
                continue
            # name
            _name = child_item.text  # 이름
            # paths
            _paths = Utils.join_path(token='#', source=sub_paths, value=_name)
            self._insert(_cid, _name, _paths)
