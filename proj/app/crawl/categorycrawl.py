import uuid

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.remote.webelement import WebElement


class CategoryCrawl(object):

    URL = 'https://shopping.naver.com/'
    DELIMITER = 'cat_id='

    category_result_map: dict = {
        'name': str,
        'parent_id': str,
        'child': list
    }

    def __init__(self, driver):
        self.driver = driver

    def _parse_cat_id(self, value: str) -> str:
        if value is not None:
            x = 0
            x = value.find(self.DELIMITER)
            if x != -1:
                x = x + len(self.DELIMITER) - 1
                return value[x + 1:len(value)]

    def _clear(self):
        self.category_result_map.clear()

    def parse(self, func):
        
        self.driver.get(self.URL)

        for li in self.driver.find_elements_by_xpath('//*[@id="home_category_area"]/div[1]/ul/li'):
            category: WebElement = li
            # className = co_menu_wear 
            class_att = category.get_attribute('class')
        
            # em Name Code - //*[@id="home_{1}}"]/em
            # em_nameXpath = '//*[@id="home_{0}"]/em/text()'.format(classAtt)

            # Root 이름
            root_name = category.text
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

            # Root -> MidChild
            childCategoryItems = element.find_elements(By.CLASS_NAME, 'co_col')
            self._clear()
            self.category_result_map['name'] = root_name
            self.category_result_map['parent_id'] = parent_id
            resultChildList = list()
            self.category_result_map['child'] = resultChildList

            childCategory: WebElement
            for childCategory in childCategoryItems:
                midCateMap = dict()

                # 중간 카테고리
                midCate : WebElement = childCategory.find_element_by_tag_name('strong')
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
                childList : WebElement = childCategory.find_elements(By.TAG_NAME, 'li')

                childItem : WebElement

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

                resultChildList.append(midCateMap)
            # 수정 해야함.
            func(self.category_result_map)
