import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webelement import WebElement

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from bs4 import BeautifulSoup
import time


def makeUrl(catId, pagingIndex):
    baseUrl = 'https://search.shopping.naver.com/search/category?catId=', '&frm=NVSHMDL&origQuery&pagingIndex=', '&pagingSize=100&productSet=model&query&sort=rel&timestamp=&viewType=list'
    return baseUrl[0] + catId + baseUrl[1] + str(pagingIndex) + baseUrl[2]


def parseFunc(index, catId):
    pagingIndex = index

    URL = makeUrl(catId, pagingIndex)

    driver = webdriver.Chrome(executable_path='chromedriver.exe')

    req = driver.page_source

    driver.get(url=URL)

    prev_height = driver.execute_script("return document.body.scrollHeight")

    last_height = driver.execute_script("return document.body.scrollHeight")
    while (True):
        for _ in range(15):
            driver.find_element_by_class_name('thumbnail_thumb__3Agq6').send_keys(Keys.SPACE)
            time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    items = driver.find_elements_by_xpath('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div')

    item: WebElement

    productInfo_arr = []

    for item in items:

        productInfoObj = {
            'productName': '상품 이름 없음',
            'key': '키값 이름 없음',
            'url': 'url 이름 없음',
            'optionInfo': {},
            'img': '이미지 없음'
        }

        productInfoObj['productName'] = item.find_element_by_class_name('basicList_link__1MaTN').text

        thumbnailObj = item.find_element_by_class_name('thumbnail_thumb__3Agq6')

        if thumbnailObj:
            try:
                element = thumbnailObj.find_element_by_tag_name('img')
            except:
                element = None

            if (element):
                productInfoObj['img'] = element.get_attribute('src')
            else:
                pass

            if (thumbnailObj.get_attribute('href')): productInfoObj['url'] = thumbnailObj.get_attribute('href')

        productInfo = item.find_element_by_class_name('basicList_detail_box__3ta3h')
        productInfoArr = productInfo.text.split('|')

        for infoItem in productInfoArr:
            if infoItem != '' and len(infoItem) > 2:
                (key, value) = infoItem.split(':')
                productInfoObj['optionInfo'][key] = value
        f.write(str(index) + ',' + productInfoObj['productName'] + ',' + productInfoObj['img'] + ',' + productInfoObj[
            'url'] + ',' + str(productInfoObj['optionInfo']) + '\n')
        productInfo_arr.append(productInfoObj)

    driver.close()


if __name__ == "__main__":

    catId = '50000100'

    f = open("parsingData.csv", "w")
    for i in range(2):
        parseFunc(i, catId)
        print('>>> parsing page: ', str(i))

    f.close()


