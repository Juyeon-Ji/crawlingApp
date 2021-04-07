'''
상품목록에서 상품 정보를 수집하는 crawler 입니다.

수집된 category의 id(cat_id)를 받아
해당 카테고리에 있는 상품을 수집합니다.
'''
import time
import logging
import random

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

from common.config.configmanager import ConfigManager, CrawlConfiguration
from common.database.dbmanager import DatabaseManager
from common.driver.seleniumdriver import Selenium


class ProductCrawl():
    '''
    상품목록에서 상품 정보를 수집하는 crawler 입니다.
    Attributes:
        driver
    '''


    def __init__(self):

        # 크롬 selenium Driver - singleton
        self.driver = Selenium().driver

        # 크롤링 설정 정보 관리 - singleton
        self.crawl_config: CrawlConfiguration = ConfigManager().crawl_config
        # Database manager - 데이터 조회 및 저장을 여기서 합니다. - singleton
        self.database_manager = DatabaseManager()

        self.paing_start:int = 0 # self.crawl_config.crawl_page_range
        self.paging_range:int = 2
        self.paging_size:int = 20  # self.crawl_config.crawl_count


        self.base_url = ['https://search.shopping.naver.com/search/category?catId=',
                        '&frm=NVSHMDL&origQuery&pagingIndex=',
                        '&pagingSize=', '&productSet=model&query&sort=rel&timestamp=&viewType=list']

        self.data = None
        self.insert_fuc = None
        self.productInfo_arr = []
        try:
            self.start_prasing_process()
        except Exception as e:
            logging.exception(e)

    def _category_generator(self):
        """:return category 목록들"""
        for item in self.crawl_config.crawl_category:
            query = self.database_manager.keyword_query('paths', item)
            yield self.database_manager.find('category', query=query)

    def start_prasing_process(self, category_info = {}, paging_index = 1):
        '''파싱 프로세스 시작'''

        # logging.debug('>>> start parsing: '
        #               , category_info['name'], 'Pg.', str(paging_index))

        self.category_id = '50000167' # category_info['cat_id']
        product_page_url = self.make_url(paging_index)
        self.scrollPage(product_page_url)
        self.parsingData()  # 파싱 된 데이터
        # self.productInfo_arr <- 파싱된 결과 값이 담긴 list
        logging.info(len(self.productInfo_arr), 'data parsed')



    def make_url(self, pagingIndex) -> str:
        '''category id, 페이지 사이즈, 페이지 넘버를 조합하여 url 생성'''
        return self.base_url[0] + self.category_id + self.base_url[1] + str(pagingIndex) + \
               self.base_url[2] + str(self.paging_size) + self.base_url[3]

    def scrollPage(self, product_page_url):
        '''스크롤 끝가지 내리기'''
        self.driver.get(url=product_page_url)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            for _ in range(15):
                self.driver.find_element_by_class_name\
                    ('thumbnail_thumb__3Agq6').send_keys(Keys.SPACE)
                time.sleep(random.uniform(3, 10)) # random
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_product_info_form(self):
        '''상품 정보를 담는 객체 formmat'''
        return {'productName': 'null', 'url': 'null',
                  'catId': 'null', 'n_id': 'null',
                  'optionInfo': {}, 'img': 'null',}

    def parsingData(self) -> list:
        '''데이터 파싱'''
        items = self.driver.find_elements_by_xpath\
                ('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div')

        time.sleep(random.uniform(3, 5))  # random

        item: WebElement

        self.productInfo_arr = []

        for item in items:

            time.sleep(random.uniform(3, 5))  # random
            product_info_form = self.get_product_info_form()


            titleObj = item.find_element_by_class_name('basicList_link__1MaTN')
            thumbnailObj = item.find_element_by_class_name('thumbnail_thumb__3Agq6')

            product_info_form['catId'] = self.category_id
            product_info_form['productName'] = titleObj.text

            if thumbnailObj:
                try:
                    element = thumbnailObj.find_element_by_tag_name('img')
                except:
                    element = None
                if element:
                    product_info_form['img'] = element.get_attribute('src')
                else:
                    pass

            if titleObj.get_attribute('href'):
                product_info_form['url'] = thumbnailObj.get_attribute('href')
                product_info_form['n_id'] = thumbnailObj.get_attribute('data-nclick').split(':')[-1]

            product_info_item = item.find_element_by_class_name('basicList_detail_box__3ta3h')
            product_info_data = product_info_item.text.split('|')

            for infoItem in product_info_data:
                if infoItem != '' and len(infoItem) > 1:
                    try:
                        (key, value) = infoItem.split(':')
                        product_info_form['optionInfo'][key] = value
                    except:
                        pass
            self.productInfo_arr.append(product_info_form)
