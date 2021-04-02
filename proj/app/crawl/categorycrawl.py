import uuid

import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

from selenium.webdriver.remote.webelement import WebElement

class CategoryCrawl(object):

    URL = 'https://shopping.naver.com/'

    def __init__(self, driver):
        self.driver = driver

    def parse(self):
        
        self.driver.get(self.URL)

        for li in self.driver.find_elements_by_xpath('//*[@id="home_category_area"]/div[1]/ul/li'):
            category : WebElement = li
            # className = co_menu_wear 
            classAtt = category.get_attribute('class')
        
            # em Name Code - //*[@id="home_{1}}"]/em
            em_nameXpath = '//*[@id="home_{0}"]/em/text()'.format(classAtt)
            # Root 이름
            rootName = category.text
            # //*[@id="home_co_menu_wear"]
            parentId = uuid.uuid4().hex

            # //*[@id="home_category_area"]/div[1]/ul/li[1]
            click_xpath = '//*[@id="home_{0}"]'.format(classAtt)

            self.driver.implicitly_wait(3)
            # 먼저 클릭해봄.
            self.driver.find_element_by_xpath(click_xpath).send_keys(Keys.ENTER)
            # classAtt에 맞춰 내부 xPath 설정
            xPath_cate = '//*[@id="home_{0}_inner"]/div[1]'.format(classAtt)

            # Root Category
            element : WebElement = None 
            while 1:
                if element is not None:
                    break

                else:
                    # 클릭 이벤트가 정상적으로 안들어오면 계속 클릭하자..
                    self.driver.find_element_by_xpath(click_xpath).send_keys(Keys.ENTER)
                    self.driver.implicitly_wait(4)
                    element = self.driver.find_element_by_xpath(xPath_cate)

            # Root -> MidChild
            childCategoryItems = element.find_elements(By.CLASS_NAME, 'co_col')

            resultChildList = list()

            childCategory : WebElement
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
                midCateMap['_id'] = uuid.uuid4().hex
                midCateMap['parentId'] = parentId
                

                # 하위 카테고리 리스트
                childList : WebElement = childCategory.find_elements(By.TAG_NAME, 'li')

                childItem : WebElement

                childItemList = list()

                for childItem in childList:
                    childItemMap = dict()

                    text = childItem.text # 이름
                    _id = childItem._id # 이건 쓰면 안되는데.. 새로 생성하던지 하자.
                    href = childItem.find_element_by_tag_name('a').get_attribute('href')
                    childItemMap['name'] = text
                    childItemMap['_id'] = _id
                    childItemMap['parentId'] = midCateMap['_id']

                    childItemList.append(childItemMap)
                    
                midCateMap['childs'] = childItemList

                resultChildList.append(midCateMap)


if __name__ in '__main__':
    pass