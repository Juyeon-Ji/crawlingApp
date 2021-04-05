import uuid
import logging
from operator import eq
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.remote.webelement import WebElement

from proj.common.driver.seleniumdriver import Selenium
from proj.common.database.dbmanager import DatabaseManager
from proj.common.config.configmanager import CrawlConfiguration, ConfigManager



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

    def _insert(self, result_dict: dict):
        """ Mongo Database Insert """
        return self.database_manager.insert_one_mongo('category', result_dict)

    def parse(self):
        self.driver.get(self.URL)

        try:
            for category in self.driver.find_elements_by_xpath('//*[@id="home_category_area"]/div[1]/ul/li'):
                result_dict = self._parse_root(category)
                # className = co_menu_wear

                if result_dict is not None:
                    self._insert('category', result_dict)


        except Exception as e:
            logging.debug(str(e))

    def _parse_root(self, category: WebElement) -> dict:
        category_result_map: dict = {
            'name': str,
            'parent_id': str,
            'child': list
        }
        category_result_map.clear()
        # Root 이름
        root_name : str = category.text

        for exclude_category in self.crawl_config.exclude_category:
            if eq(root_name, exclude_category):
                return None

        class_att = category.get_attribute('class')

        logging.info('rootName : ' + root_name)
        # //*[@id="home_co_menu_wear"]
        parent_id = uuid.uuid4().hex

        # //*[@id="home_category_area"]/div[1]/ul/li[1]
        click_xpath = '//*[@id="home_{0}"]'.format(class_att)

        self.driver.implicitly_wait(3)
        # 먼저 클릭해봄.
        self.driver.find_element_by_xpath(click_xpath).send_keys(Keys.ENTER)
        # classAtt에 맞춰 내부 xPath 설정
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

        category_result_map['name'] = root_name
        category_result_map['parent_id'] = parent_id
        # Root -> MidChild
        childCategoryItems = element.find_elements(By.CLASS_NAME, 'co_col')

        category_result_map['child'] = self._parse_child_category(childCategoryItems, parent_id)

        return category_result_map

    def _parse_child_category(self, child_category_list, parent_id) -> list:
        result_item_list = list()

        childCategory: WebElement
        for childCategory in child_category_list:
            midCateMap = dict()

            # 중간 카테고리
            midCate: WebElement = childCategory.find_element_by_tag_name('strong')
            # name
            mid_name = midCate.find_element_by_tag_name('a').text
            # href
            mid_href = midCate.find_element_by_tag_name('a').get_attribute('href')

            midCateMap['name'] = mid_name
            midCateMap['href'] = mid_href
            midCateMap['cat_id'] = self._parse_cat_id(mid_href)

            midCateMap['_id'] = uuid.uuid4().hex
            midCateMap['parentId'] = parent_id

            # 하위 카테고리 리스트
            childList: WebElement = childCategory.find_elements(By.TAG_NAME, 'li')

            childItem: WebElement

            childItemList = list()

            for childItem in childList:
                childItemMap = dict()

                text = childItem.text  # 이름
                _id = childItem._id  # 이건 쓰면 안되는데.. 새로 생성하던지 하자.
                href = childItem.find_element_by_tag_name('a').get_attribute('href')

                childItemMap['name'] = text
                childItemMap['_id'] = _id
                childItemMap['href'] = href
                childItemMap['cat_id'] = self._parse_cat_id(href)
                childItemMap['parentId'] = midCateMap['_id']

                childItemList.append(childItemMap)

            midCateMap['childs'] = childItemList

            result_item_list.append(midCateMap)

        return result_item_list
