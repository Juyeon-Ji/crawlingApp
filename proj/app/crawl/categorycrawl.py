import uuid
import logging
from operator import eq
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.remote.webelement import WebElement

from proj.common.driver.seleniumdriver import Selenium
from proj.common.database.dbmanager import DatabaseManager
from proj.common.config.configmanager import CrawlConfiguration, ConfigManager


def _join_path(token, source: str, value: str) -> str:
    return token.join([source, value])


class CategoryCrawl(object):
    URL = 'https://shopping.naver.com/'
    DELIMITER = 'cat_id='

    def __init__(self):
        # 크롬 selenium Driver - singleton
        self.driver = Selenium().driver
        # 크롤링 설정 정보 관리 - singleton
        self.crawl_config: CrawlConfiguration = ConfigManager().crawl_config_object
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
        _category_document: dict = None

        _category_document['cid'] = cid
        _category_document['name'] = name
        _category_document['paths'] = paths

        return self.database_manager.insert_one_mongo('category', _category_document)

    def parse(self):
        self.driver.get(self.URL)

        try:
            for category in self.driver.find_elements_by_xpath('//*[@id="home_category_area"]/div[1]/ul/li'):
                self._parse_root(category)

        except Exception as e:
            logging.error(str(e))

    def _parse_root(self, category: WebElement):
        self._category_document.clear()

        # Root 이름
        root_name: str = category.text
        logging.info('rootName : ' + root_name)

        for exclude_category in self.crawl_config.exclude_category:
            if eq(root_name, exclude_category):
                return None

        class_att = category.get_attribute('class')
        click_xpath = '//*[@id="home_{0}"]'.format(class_att)

        self.driver.implicitly_wait(3)
        # 먼저 클릭해봄.
        self.driver.find_element_by_xpath(click_xpath).send_keys(Keys.ENTER)
        # class_att 맞춰 내부 xPath 설정
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
                element = self.driver.find_element_by_xpath(xpath_cate)

        # Root -> sub
        sub_category = element.find_elements(By.CLASS_NAME, 'co_col')

        self._parse_sub(sub_category, root_name)

    def _parse_sub(self, sub_category, root_name):
        sub_item: WebElement
        for sub_item in sub_category:
            # 중간 카테고리
            sub_element: WebElement = sub_item.find_element_by_tag_name('strong')
            # name
            _name = sub_element.find_element_by_tag_name('a').text
            # paths
            _paths = _join_path(',', root_name, _name)
            # href
            sub_href = sub_element.find_element_by_tag_name('a').get_attribute('href')
            # cid
            _cid = self._parse_cat_id(sub_href)
            # cid, name, paths
            self._insert(_cid, _name, _paths)

            # 하위 카테고리 리스트
            child_items: WebElement = sub_item.find_elements(By.TAG_NAME, 'li')
            self._parse_child(child_items, _paths)

    def _parse_child(self, child_items, sub_paths):
        child_item: WebElement
        for child_item in child_items:
            # name
            _name = child_item.text  # 이름
            # paths
            _paths = _join_path(',', sub_paths, _name)
            # href
            _href = child_item.find_element_by_tag_name('a').get_attribute('href')
            # cid
            _cid = self._parse_cat_id(_href)

            self._insert(_cid, _name, _paths)
