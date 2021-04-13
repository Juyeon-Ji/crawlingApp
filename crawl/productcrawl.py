'''
상품목록에서 상품 정보를 수집하는 crawler 입니다.

수집된 category의 id(cat_id)를 받아
해당 카테고리에 있는 상품을 수집합니다.
'''
import logging
import datetime
import time

import requests
import re
import json
from bs4 import BeautifulSoup  # BeautifulSoup import

from common.config.configmanager import ConfigManager, CrawlConfiguration
from common.database.dbmanager import DatabaseManager

from common.util import Utils

class ProductCrawl:
    '''
    상품목록에서 상품 정보를 수집하는 crawler 입니다.
    Attributes:
        driver
    '''
    PRODUCT_COLLECTION = "product"
    CRAWL_CONFIG_COLLECTION = "crawl_config"

    _excepted_data_count = 0

    def __init__(self):

        logging.info('start product crawl')
        # Database manager - 데이터 조회 및 저장을 여기서 합니다. - singleton
        self.database_manager = DatabaseManager()

        # start Page Default
        self._paging_start: int = 1
        self._paging_range: int = 2#self.crawl_config.crawl_page_range
        self._view_size: int = 20 # self.crawl_config.crawl_count


        # 먼저 확인해야함. 다시 수집시 DB->Config 정보 셋
        # TODO: 나중에 처리하도록 수정
        # self._check_crawl_configuration()

        self._result: list = []

        self._category: dict = None

        self.productInfo_arr = []
        self._current_page: int = 0
        self.last_crawled_date_time = datetime.datetime.now()



    def _check_crawl_configuration(self):
        """Config 정보 set"""
        _config: dict = self.database_manager.find_one(self.CRAWL_CONFIG_COLLECTION)

        if _config.get('start_page') is not None:
            self._paging_start = _config['start_page']

        if _config.get('crawl_category_list') is not None:
            self.crawl_config.crawl_category = _config['crawl_category_list']



    def _category_getter(self) -> list:
        """ 카테고리 목록 조회해서 분석
        :return category 목록들"""
        _categories: list = []
        for item in self.crawl_config.crawl_category:
            query = self.database_manager.keyword_query('paths', item)
            _categories.extend(list(self.database_manager.find('category', query=query)))

        return _categories

    def parse(self):
        ''' 외부에서 파싱을 하기 위해 호출하는 함수'''
        # 카테고리 데이터 가져오기 임시 데이터
        # _categories: list = self._category_getter()
        #
        # for category in _categories:
        #     self._category = category
        #
        #     self.start_parsing_process()

        # 카테고리 샘플 데이터
        self._category = {
            'cid': '50000158',
            '_id': '50000158',
            'paths': '생활/건강>문구/사무용품',
            'name': '문구사무용품'
        }

        self._start_parsing_process()

    def _start_parsing_process(self):
        """파싱 프로세스 시작"""
        self._current_page = 0

        for page_number in range(1, 101):
            time.sleep(0.5)
            try:
                _url = self.make_url(page_number)
                _headers = {'Content-Type': 'application/json;'}

                logging.info(">>> URL : " + _url)

                logging.info('>>> start parsing: ' + self._category.get('name') + ' Pg.' + str(page_number))
                req = requests.get(_url, _headers)

                self.parsing_data(self._get_product_data(req))

                self._current_page = page_number
            except Exception as e:
                logging.debug(">>> Category Collect Err " + str(self._current_page)
                              + "  name: " + self._category.get('name') + "  Err :" + str(e))

        logging.info('>>> end childCategory: ' + self._category.get('name') + ' Pg.' + str(self._current_page))

    def _get_product_data(self, req) -> dict:
        '''
        상품 정보 가져오기
        :arg
        :param req: request 정보
        :return: data_dict 상품 정보
        '''
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')  # html.parser를 사용해서 soup에 넣겠다

        json_data = soup.find('script', text=re.compile('application/json'))

        data_dict = json.loads(str(json_data.contents[0]))

        return data_dict

    def parsing_data(self, data_dict):
        ''' 데이터 파싱 '''
        product_info: dict = data_dict.get('props').get('pageProps').get('initialState').get('products')
        if product_info is not None:
            '''수집된 데이터가 있는 경우'''

            product_list: list = product_info.get('list')
            product_total_count: dict = product_info.get('total')

            products_data: list()
            self._excepted_data_count = 0

            logging.info("수집 시작 - 상품 데이터 수: " + str(len(product_list)))
            if len(product_list) >0:
                for product in product_list:
                    product_data: dict()

                    product_item = product.get('item')
                    if product_item.get('adId') is None:
                        '''광고 데이터가 아닌 경우에만 수집'''

                        product_data = self._set_category_info(product_data) # 카테고리 정보 Setting
                        product_data = self._set_product_info(product_data, product_item) # 상품 정보 Setting

                        self._insert_product_info(product_info)
                        products_data.append(product_data)
                    else:
                        self._excepted_data_count += 1
            else:
                logging.error('!!! Exception: 상품 정보가 없습니다.')
            if len(product_list) != len(products_data) + self._excepted_data_count:
                logging.error("!!! Exception: 데이터 수 확인이 필요 합니다.")
                logging.info("수집된 데이터 수: " + str(len(products_data)))
                logging.info("수집 제외된 데이터 수: " + str(self._excepted_data_count))
        else:
            logging.error('!!! Exception: 데이터가 수집되지 않았습니다.')

    def _set_category_info(self, product_data: dict) -> dict:
        '''상품정보에 카테고리 정보 셋팅
            arg:
                products_data: 상품 정보 객체
        '''
        product_data['n_cid'] = self._category.get('cid')
        product_data['cid'] = self._category.get('_id')
        product_data['paths'] = self._category.get('paths')
        product_data['cname'] = self._category.get('name')
        return product_data

    def _set_product_info(self, product_data: dict, product_item):

        product_data['id'] = product_item.get('id')
        product_data['imageUrl'] = product_item.get('imageUrl')
        product_data['productTitle'] = product_item.get('productTitle')

        product_data['option'] = {}

        if product_item.get('attributeValue') is not None:
            # 옵션 정보가 있는 경우
            product_option_key: list  = product_item.get('attributeValue').split('|') # 옵션 키값
            product_option_value: list = product_item.get('characterValue').split('|') # 옵션 벨류값

            product_data['option'] = dict(zip(product_option_key, product_option_value))

        return product_data

    def _insert_product_info(self, value: dict):
        """db data insert"""
        try:
            # TODO: 값 비교는 어디서 하지?
            _selection = self.database_manager.find_query("n_id", value.get("n_id"))
            self.database_manager.update(self.PRODUCT_COLLECTION, _selection, value)
        except Exception as e:
            logging.error('!!! Fail: Insert data to DB: ', e)

    def _upsert_crawl_configuration(self, start_page):
        """모든 분석이 끝나고 Config 정보 update"""
        # 조건
        _filter = {}
        # 변경 데이터
        _config = dict()
        _config['start_page'] = start_page

        self.database_manager.update(self.CRAWL_CONFIG_COLLECTION, _filter, _config)

    def make_url(self, paging_index) -> str:
        """category id, 페이지 사이즈, 페이지 넘버를 조합하여 url 생성"""
        _url = ("https://search.shopping.naver.com/search/category?catId={0}&frm=NVSHMDL&origQuery&pagingIndex={1}&pagingSize={2}&productSet=model&query&sort=rel&timestamp=&viewType=list")
        _cid = self._category['cid']
        return _url.format(_cid, paging_index, self._view_size)
