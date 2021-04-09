import unittest

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys


import time

    def test_get_category_id_from_data(self):
        '''dictionary data format 조회'''

        for category_info in categories_info_obj:
            self.category_id = category_info['cid']

            self.start_prasing_process()

    # 카테고리 데이터 가져오기 끝

    def start_prasing_process(self):
        '''파싱 프로세스 시작'''
        # self.f = open("parsingData.csv", "w")
        for page_number in self.get_page_number():
            crawled_items = self.setting_for_parsing(page_number)

            self.take_a_sleep(2, 4)

            self.parsing_data(crawled_items)
        # self.f.close()

    def setting_for_parsing(self, page_number) -> [WebElement]:
        '''크롤링하기 위하 사전 작업: 스크롤 내리기, html 클롤링'''

        logging.info('>>> start parsing: '
                     + self.category_id + ' Pg.' + str(page_number))

        logging.info('>>> start scroll down')
        self.scroll_page_to_bottom(self.make_url(page_number))
        logging.info('>>> start parsing')
        return self.crawling_html()

    def get_page_number(self) -> int:
        '''파싱 시작페이지 ~ 파싱 페이지 끝까지 페이지 넘버 넘겨주기'''
        for page_number in range(self.paing_start, self.paing_start + self.paging_range):
            yield page_number

    def make_url(self, paging_index) -> str:
        '''category id, 페이지 사이즈, 페이지 넘버를 조합하여 url 생성'''
        return self.base_url[0] + self.category_id + self.base_url[1] + str(paging_index) + \
               self.base_url[2] + str(self.paging_size) + self.base_url[3]

    def scroll_page_to_bottom(self, product_page_url):
        '''스크롤 끝가지 내리기'''
        self.driver.get(url=product_page_url)

        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            for _ in range(15):
                self.driver.find_element_by_class_name \
                    ('thumbnail_thumb__3Agq6').send_keys(Keys.SPACE)
                self.take_a_sleep(2, 8)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def crawling_html(self) -> [WebElement]:
        '''데이터 파싱'''
        crawled_items: [WebElement] = self.driver.find_elements_by_xpath \
            ('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div')

        return crawled_items

    def parsing_data(self, items: [WebElement]):
        for item in items:
            self.take_a_sleep(1, 3)

            product_info_form: dict = self.setting_product_info_form(item)

            product_info_data_items: list = self.get_product_detail_info_items(item)
            product_info_form: dict = self.parsing_product_detail_info(product_info_data_items, product_info_form)

            logging.debug(product_info_form)
            self.insert_data_to_db(product_info_form)  # db insert

    def get_product_detail_info_items(self, item) -> list:
        '''크롤링 된 html에서 상품정보를 갖고 있는 객체 가져오기'''
        product_info_item = item.find_element_by_class_name('basicList_detail_box__3ta3h')
        self.driver.execute_script("arguments[0].style.overflow = 'visible';", product_info_item)
        self.take_a_sleep(3, 5)
        # product_info_data_items = product_info_item.find_elements_by_class_name('basicList_detail__27Krk')

        # basicList_detail__27Krk
        return product_info_item

    def insert_data_to_db(self, data: dict):
        '''db data insert'''
        try:
            if self.database_manager.count_document_exists('product', 'nid', data):  # 해당 상품이 DB에 존재 하는 경우
                logging.info('data exist', data)
            else:
                self.database_manager.find('product', 'nid', data)

        except Exception as e:
            logging.error('!!! Fail: Insert data to DB: ', e)

    def _update(self, cid, name, paths: str):
        _query = self.database_manager.find_query('cid', cid)

        _update_data = dict()
        _update_data['name'] = name
        _update_data['paths'] = paths
        _update_data['update_time'] = datetime.now()

        return self.database_manager.update(self.COLLECTION, _query, {"&set": _update_data})

    def parsing_product_detail_info(self, product_info_data_items, product_info_form) -> dict:
        '''text로 수집된 데이터 ':'로 split 하여 dictionary 형태로 저장'''
        product_info_datas = product_info_data_items.text.split('|')
        for data in product_info_datas:
            # print(info_obj.text)
            info_data: list = data.split(":")
            if len(info_data) > 1:
                (key, value) = info_data
                product_info_form['optionInfo'][key] = value

        # sampel_data = [product_info_form['catId'], product_info_form['productName'], product_info_form['img'],
        #                product_info_form['n_id'], product_info_form['url'], str(product_info_form['optionInfo'])]
        # tmpData = self.make_csvForm(sampel_data)
        # self.f.write(tmpData)

        return product_info_form

    # 상품 정보 담는 객체 Setting 시작
    def setting_product_info_form(self, item) -> dict:
        '''파싱된 데이터 json 포멧에 맞게 넣도록 Setting
            img link, 상품 상세정보 link, 상품 naver id'''

        product_info_form = self.init_product_info_form()

        titleObj = item.find_element_by_class_name('basicList_link__1MaTN')
        thumbnailObj = item.find_element_by_class_name('thumbnail_thumb__3Agq6')

        return self.set_product_info_form(product_info_form, titleObj, thumbnailObj)

    def init_product_info_form(self) -> dict:
        '''상품 정보를 담는 객체 formmat'''
        return {'productName': 'null', 'url': 'null',
                'catId': 'null', 'n_id': 'null',
                'optionInfo': {}, 'img': 'null', }

    def set_product_info_form(self, product_info_form, titleObj, thumbnailObj) -> dict:
        '''파싱된 데이터 json 포멧에 맞게 넣기
            img link, 상품 상세정보 link, 상품 naver id'''
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

        return product_info_form

    # 상품 정보 담는 객체 Setting 끝

    def take_a_sleep(self, s: int, e: int):
        '''S ~ E 사이의 랜던값으로 Sleep'''
        random_count = random.uniform(s, e)
        logging.info('take a sleep: ' + str(random_count))
        time.sleep(random_count)  # random

    def get_sample_category_data(self):
        return [{'_id': '', 'cid': '50001421', 'name': '에어컨', 'paths': ''}]

    # def make_csvForm(self, dataArr: list) -> str:
    #     '''csv form 작성'''
    #     tmpStr: str = ''
    #     i = 0
    #     for data in dataArr:
    #         if (i + 1 == len(dataArr)):
    #             tmpData = str(data) + '\n'
    #
    #         else:
    #             tmpData = str(data) + ','
    #         tmpStr += tmpData
    #         i += 1
    #     return tmpStr





if __name__ == '__main__':
    unittest.main()
