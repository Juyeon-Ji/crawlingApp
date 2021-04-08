'''
상품목록에서 상품 정보를 수집하는 crawler 입니다.

수집된 category의 id(cat_id)를 받아
해당 카테고리에 있는 상품을 수집합니다.
'''
import logging
import datetime

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

from common.util import Utils
from common.config.configmanager import ConfigManager, CrawlConfiguration
from common.database.dbmanager import DatabaseManager
from common.driver.seleniumdriver import Selenium



class ProductCrawl:
    '''
    상품목록에서 상품 정보를 수집하는 crawler 입니다.
    Attributes:
        driver
    '''
    PRODUCT_COLLECTION = "product"
    CRAWL_CONFIG_COLLECTION = "crawl_config"

    def __init__(self):

        logging.info('start product crawl')
        # 크롬 selenium Driver - singleton
        self.driver = Selenium().driver

        # 크롤링 설정 정보 관리 - singleton
        self.crawl_config: CrawlConfiguration = ConfigManager().crawl_config
        # Database manager - 데이터 조회 및 저장을 여기서 합니다. - singleton
        self.database_manager = DatabaseManager()

        # start Page Default
        self._paging_start: int = 1
        self._paging_range: int = self.crawl_config.crawl_page_range
        self._view_size: int = self.crawl_config.crawl_count

        self.base_url = "https://search.shopping.naver.com/search/category?catId={0} \
                 &frm=NVSHMDL&origQuery&pagingIndex={1}&pagingSize={2}&productSet=model \
                 &query&sort=rel&timestamp=&viewType=list"

        # self.base_url = ['https://search.shopping.naver.com/search/category?catId=',
        #                 '&frm=NVSHMDL&origQuery&pagingIndex=',
        #                 '&pagingSize=', '&productSet=model&query&sort=rel&timestamp=&viewType=list']

        # 먼저 확인해야함. 다시 수집시 DB->Config 정보 셋
        self._check_crawl_configuration()

        self._result: list = []

        self._cid = None

        self.productInfo_arr = []
        self.last_crawled_date_time = datetime.datetime.now()

    # TODO : 값 비교 작업 여기서 해주세요.
    def _insert_product_info(self, data: dict):
        """db data insert"""
        try:
            self.database_manager.find('product', {'nid': data})
        except Exception as e:
            logging.error('!!! Fail: Insert data to DB: ', e)

    def _check_crawl_configuration(self):
        """Config 정보 set"""
        _config = self.database_manager.find_one(self.CRAWL_CONFIG_COLLECTION)
        self._paging_start = _config['start_page']
        self.crawl_config.crawl_category = _config['crawl_category_list']

    def _upsert_crawl_configuration(self, start_page):
        """모든 분석이 끝나고 Config 정보 update"""
        # 조건
        _filter = {}
        # 변경 데이터
        _config = dict()
        _config['start_page'] = start_page

        self.database_manager.update(self.CRAWL_CONFIG_COLLECTION, _filter, _config)

    def _category_getter(self) -> list:
        """ 카테고리 목록 조회해서 분석
        :return category 목록들"""
        _categories: list = []
        for item in self.crawl_config.crawl_category:
            query = self.database_manager.keyword_query('paths', item)
            _categories.extend(list(self.database_manager.find('category', query=query)))

        return _categories

    def parse(self):
        _categories: list = self._category_getter()
        try:
            for category in _categories:
                self._cid = category['cid']

                self.start_parsing_process()

        except Exception as e:
            logging.debug(e)

    def start_parsing_process(self):
        """파싱 프로세스 시작"""
        for page_number in self.get_page_number():
            _url = self.make_url(page_number)
            self.driver.get(url=_url)

            logging.info('>>> start parsing: ' + self._cid + ' Pg.' + str(page_number))

            self.scroll_page_to_bottom()

            Utils.take_a_sleep(2, 4)

            self.parsing_data(self.crawling_html())

    def get_page_number(self) -> int:
        '''파싱 시작페이지 ~ 파싱 페이지 끝까지 페이지 넘버 넘겨주기'''
        # 변수 검증만 해보면됨.
        for page_number in range(self._paging_start, self._paging_start + self._paging_range):
            yield page_number

    def make_url(self, paging_index) -> str:
        """category id, 페이지 사이즈, 페이지 넘버를 조합하여 url 생성"""
        return self.base_url.format(self._cid, paging_index, self._view_size)

    def scroll_page_to_bottom(self):
        """스크롤 끝가지 내리기"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:

            for _ in range(15):
                self.driver.find_element_by_class_name('thumbnail_thumb__3Agq6').send_keys(Keys.SPACE)
                Utils.take_a_sleep(2, 8)

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def crawling_html(self) -> [WebElement]:
        """데이터 파싱"""
        crawled_items: [WebElement] = self.driver.find_elements_by_xpath(
            '//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div'
        )

        return crawled_items

    def parsing_data(self, products: [WebElement]):
        for product in products:
            Utils.take_a_sleep(1, 3)
            # 내부에서 dict 생성
            product_info_form: dict = self._parsing_product_base_info(product)

            product_info_form: dict = self.parsing_product_detail_info(
                self.get_product_detail_info_items(product), product_info_form
            )
            # TODO: 1개씩 넣을꺼면 여기서 Insert하세요.
            # TODO: 모아서 하려면 list에 값을 담아서 for밖에서 넣어주세요.
            self._insert_product_info(product_info_form)

    def get_product_detail_info_items(self, item) -> WebElement:
        """크롤링 된 html에서 상품정보를 갖고 있는 객체 가져오기"""

        product_info_item = item.find_element_by_class_name('basicList_detail_box__3ta3h')
        self.driver.execute_script("arguments[0].style.overflow = 'visible';", product_info_item)
        Utils.take_a_sleep(3, 5)
        # List -> WebElement 로 변경함.
        # product_info_data_items = product_info_item.find_elements_by_class_name('basicList_detail__27Krk')
        # basicList_detail__27Krk
        return product_info_item

    def parsing_product_detail_info(self, product_info_data_item, product_info_form) -> dict:
        """text로 수집된 데이터 ':'로 split 하여 dictionary 형태로 저장"""
        product_info_datas = product_info_data_item.text.split('|')
        for data in product_info_datas:
            # print(info_obj.text)
            info_data: list = data.split(":")
            if len(info_data) > 1:
                (key, value) = info_data
                product_info_form['optionInfo'][key] = value

        return product_info_form

    # TODO: 정리가 필요할듯.
    def _parsing_product_base_info(self, item) -> dict:
        """파싱된 데이터 json 포멧에 맞게 넣도록 Setting
            img link, 상품 상세정보 link, 상품 naver id"""
        product_info_form: dict = {}

        title_element = item.find_element_by_class_name('basicList_link__1MaTN')
        thumbnail_element = item.find_element_by_class_name('thumbnail_thumb__3Agq6')

        product_info_form['catId'] = self._cid
        product_info_form['productName'] = title_element.text

        if thumbnail_element:
            try:
                element = thumbnail_element.find_element_by_tag_name('img')
            except Exception as e:
                element = None
            if element:
                product_info_form['img'] = element.get_attribute('src')
            else:
                pass

        # TODO: 여기 확인필요
        if title_element.get_attribute('href'):
            product_info_form['url'] = thumbnail_element.get_attribute('href')
            product_info_form['n_id'] = thumbnail_element.get_attribute('data-nclick').split(':')[-1]

        return product_info_form
