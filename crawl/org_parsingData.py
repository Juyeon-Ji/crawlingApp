# 크롤러 단독 실행 가능 파일
import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys

# from proj.common.driver.seleniumdriver import Selenium
# 통합 실행 용
# from proj.common.config.configmanager import ConfigManager, CrawlConfiguration
# from proj.common.database.dbmanager import DatabaseManager

# 개별 Test용
from selenium.webdriver.chrome.options import Options

import logging


class ProductCrawl():
    url: str
    cat_id: str
    catId: str

    def __init__(self):
        CHROMEDRIVER_PATH = r'C:\Users\지주연\PycharmProjects\crawlingApp\proj\resource\chromedriver.exe'
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-gpu")

        self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        self.f = open("parsingData.csv", "w")


        self.paging_count = 2 # self.crawl_config.crawl_page_range
        self.pagingSize = 20 # self.crawl_config.crawl_count


        self.baseUrl = ['https://search.shopping.naver.com/search/category?catId=',
                        '&frm=NVSHMDL&origQuery&pagingIndex=',
                        '&pagingSize=', '&productSet=model&query&sort=rel&timestamp=&viewType=list']


        self.data = None

        self.insert_fuc = None

        self.data = self.get_sample_category_data()

        try:
            self.get_bigCategory_data()
        except Exception as e:
            print('Exception: ', e)
            # logging.exception(e)

        logging.info("driver close ")
        self.driver.close()
        logging.info("driver quit")
        self.driver.quit()
        logging.info("driver quit end")
        self.f.close()


    def get_bigCategory_data(self) -> None:
        '''큰 카테고리의 id로 조회'''
        # logging.info('큰 카테고리 수집 시작')
        for category in self.data:
            for bigCategory in category['child']:
                for i in range(self.paging_count):
                    print('>>> parsing page: ', bigCategory['name'], str(i))
                    self.startPrasingProcess(bigCategory['cat_id'], i)
                    # logging.debug('>>> parsing page: ', bigCategory['name'], str(i))

    def get_detailCategory_data(self):
        '''큰 카테고리의 하위 카테고리의 id로 조회'''
        # logging.info('큰 카테고리의 하위 카테고리 수집 시작')
        for category in self.data:
            for i in range(self.paging_count):
                # logging.debug('>>> parsing page: ', detailCategory['name'], str(i))
                self.startPrasingProcess(category['cid'], i)

    def startPrasingProcess(self, catId, paginIndex):
        self.catId = catId
        productPage_url = self.makeUrl(paginIndex)
        # logging.info('makeUrl: ', productPage_url)
        self.scrollPage(productPage_url)
        # logging.info('end scroll')
        data = self.parsingData()  # 파싱 된 데이터
        print('end parsing',data)
        # logging.info('end parsing',len(data))

        # 통합 실행 시 데이터 넣기
        # self.insert_fuc('product', data)


    def makeUrl(self, pagingIndex) -> str:
        # return self.baseUrl[0] + self.catId + self.baseUrl[1] + str(pagingIndex) + self.baseUrl[2]
        return self.baseUrl[0] + self.catId + self.baseUrl[1] + str(pagingIndex) + \
               self.baseUrl[2] + str(self.pagingSize) + self.baseUrl[3]

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

    def parsingData(self) -> list:
        '''데이터 파싱'''
        items = self.driver.find_elements_by_xpath('//*[@id="__next"]/div/div[2]/div/div[3]/div[1]/ul/div/div')

        item: WebElement

        productInfo_arr = []

        for item in items:

            productInfoObj = {'productName': 'null',
                'key': 'null',
                'url': 'null',
                'catId': 'null',
                'n_id':'null',
                'optionInfo': {},
                'img': 'null' }


            titleObj = item.find_element_by_class_name('basicList_link__1MaTN')
            thumbnailObj = item.find_element_by_class_name('thumbnail_thumb__3Agq6')

            item.find_element_by_class_name('ad_ad_stk__12U34').text

            # find_elements_by_css_selector
            self.driver.find_element_by_class_name('#basicList_price_area__1UXXR')
            productInfoObj['catId'] = self.catId
            productInfoObj['productName'] = titleObj.text

            if thumbnailObj:
                try:
                    element = thumbnailObj.find_element_by_tag_name('img')
                except:
                    element = None
                if (element):
                    productInfoObj['img'] = element.get_attribute('src')
                else:
                    pass

            if (titleObj.get_attribute('href')):
                productInfoObj['url'] = thumbnailObj.get_attribute('href')
                productInfoObj['n_id'] = thumbnailObj.get_attribute('data-nclick').split(':')[-1]

            productInfo = item.find_element_by_class_name('basicList_detail_box__3ta3h')
            productInfoArr = productInfo.text.split('|')

            for infoItem in productInfoArr:
                if infoItem != '' and len(infoItem) > 1:
                    try:
                        (key, value) = infoItem.split(':')
                        productInfoObj['optionInfo'][key] = value
                    except:
                        pass

            # f.write(
            #     str(index) + ',' + productInfoObj['productName'] + ',' + productInfoObj['img'] + ',' + productInfoObj[
            #         'url'] + ',' + str(productInfoObj['optionInfo']) + '\n')

            # 개별 테스트 시 데이터 파일 생성
            sampel_data = [productInfoObj['catId'],productInfoObj['productName'], productInfoObj['img'],
                           productInfoObj['n_id'], productInfoObj['url'], str(productInfoObj['optionInfo'])]

            tmpData = self.make_csvForm(sampel_data)
            self.writeFile(tmpData)

            productInfo_arr.append(productInfoObj)
        return productInfo_arr

    def writeFile(self, data):
        '''파일 작성'''
        self.f.write(data)

    def make_csvForm(self, dataArr: list) -> str:
        '''csv form 작성'''
        tmpStr: str = ''
        i = 0
        for data in dataArr:
            if (i + 1 == len(dataArr)):
                tmpData = str(data) + '\n'

            else:
                tmpData = str(data) + ','
            tmpStr += tmpData
            i += 1
        return tmpStr


def get_sample_category_data(self):
    return [{'_id': '', 'cid': '50000158', 'name': '문구/사무용품', 'paths': ''}]


if __name__ == '__main__':

    pro = ProductCrawl()
