import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from proj.common.config.configmanager import CrawlConfiguration
from proj.common.driver.seleniumdriver import Selenium
from proj.common.config.configmanager import ConfigManager, CrawlConfiguration
from proj.common.database.dbmanager import DatabaseManager


class ProductCrawl:
    url: str
    cat_id: str

    def __init__(self):
        # 크롬 selenium Driver - singleton
        self.driver = Selenium().driver
        # 크롤링 설정 정보 관리 - singleton
        self.crawl_config: CrawlConfiguration = ConfigManager().crawl_config_object
        # Database manager - 데이터 조회 및 저장을 여기서 합니다. - singleton
        self.database_manager = DatabaseManager()

        self.paging_count = self.crawl_config.crawl_page_range

        self.baseUrl = ['https://search.shopping.naver.com/search/category?catId=',
                        '&frm=NVSHMDL&origQuery&pagingIndex=',
                        '&pagingSize={0}&productSet=model&query&sort=rel&timestamp=&viewType=list'.format(
                            self.crawl_config.crawl_count)
                        ]

        self.data = None

        self.insert_fuc = None

        self.get_bigCategory_data()

    def get_bigCategory_data(self):
        '''큰 카테고리의 id로 조회'''
        print('카테고리')
        for category in self.data:
            for bigCategory in category['child']:
                for i in range(self.paging_count):
                    self.startPrasingProcess(bigCategory['cat_id'], i)
                    print('>>> parsing page: ', bigCategory['name'], str(i))

    def get_detailCategory_data(self):
        '''큰 카테고리의 하위 카테고리의 id로 조회'''
        for category in self.data:
            for bigCategory in category['child']:
                for detailCategory in bigCategory['child']:
                    for i in range(self.paging_count):
                        self.startPrasingProcess(detailCategory['cat_id'], i)

    def startPrasingProcess(self, catId, paginIndex):
        productPage_url = self.makeUrl(catId, paginIndex)
        self.scrollPage(productPage_url)
        data = self.parsingData()  # 파싱 된 데이터
        self.insert_fuc('product', data)

    def makeUrl(self, catId, pagingIndex) -> str:
        return self.baseUrl[0] + catId + self.baseUrl[1] + str(pagingIndex) + self.baseUrl[2]

    def scrollPage(self, productPage_url):
        '''스크롤 끝가지 내리기'''
        self.driver.get(url=productPage_url)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while (True):
            for _ in range(15):
                self.driver.find_element_by_class_name('thumbnail_thumb__3Agq6').send_keys(Keys.SPACE)
                time.sleep(1)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def parsingData(self):
        '''데이터 파싱'''
        items = self.driver.find_elements_by_xpath('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div')

        item: WebElement

        productInfo_arr = []

        for item in items:

            productInfoObj = {'productName': '상품 이름 없음',
                'key': '키값 이름 없음',
                'url': 'url 이름 없음',
                'optionInfo': {},
                'img': '이미지 없음' }

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
            # f.write(
            #     str(index) + ',' + productInfoObj['productName'] + ',' + productInfoObj['img'] + ',' + productInfoObj[
            #         'url'] + ',' + str(productInfoObj['optionInfo']) + '\n')
            productInfo_arr.append(productInfoObj)
        return productInfo_arr
