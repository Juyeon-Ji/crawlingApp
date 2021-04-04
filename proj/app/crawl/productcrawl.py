import time

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from proj.common.config.configmanager import CrawlConfiguration

class ProductCrawl:
    url: str
    cat_id: str

    def __init__(self, driver, json_data, func, crawl_config):
        # CHROMEDRIVER_PATH = r'C:\Users\지주연\PycharmProjects\crawlingApp\proj\resource\chromedriver.exe'
        # chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.add_argument("--disable-gpu")
        # # chrome_options.add_argument( f"--window-size={ WINDOW_SIZE }" )
        #
        # self.driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)
        self.driver = driver
        self.crawl_config: CrawlConfiguration = crawl_config
        self.paging_count = 1;
        self.baseUrl = ['https://search.shopping.naver.com/search/category?catId=',
                        '&frm=NVSHMDL&origQuery&pagingIndex=',
                        '&pagingSize=40&productSet=model&query&sort=rel&timestamp=&viewType=list']

        self.data = json_data
        self.insert_fuc = func

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
        return  productInfo_arr

    def getData(self):
        return [{
            "name": "패션의류",
            "parent_id": "9b56f6852baa42d8bcaee8b0caddf3fb",
            "child": [
                {
                    "name": "여성의류전체보기",
                    "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000167",
                    "cat_id": "50000167",
                    "_id": "dd94754e0d63406782ca5b687c36e6d0",
                    "parentId": "9b56f6852baa42d8bcaee8b0caddf3fb",
                    "childs": [
                        {
                            "name": "니트/스웨터",
                            "_id": "0f54fe7d-aa68-486f-872e-370b0f193732",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000805",
                            "cat_id": "50000805",
                            "parentId": "dd94754e0d63406782ca5b687c36e6d0"
                        },
                        {
                            "name": "정장세트",
                            "_id": "58c4cfe1-4afb-4160-85be-f66846778a57",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000816",
                            "cat_id": "50000816",
                            "parentId": "dd94754e0d63406782ca5b687c36e6d0"
                        }
                    ]
                },
                {
                    "name": "남성의류전체보기",
                    "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000169",
                    "cat_id": "50000169",
                    "_id": "3fcd4b506ad542cbaf6131caa6e9e6f9",
                    "parentId": "9b56f6852baa42d8bcaee8b0caddf3fb",
                    "childs": [
                        {
                            "name": "니트/스웨터",
                            "_id": "11a4c534-d0fd-485a-9c49-a6e605b0e447",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000831",
                            "cat_id": "50000831",
                            "parentId": "3fcd4b506ad542cbaf6131caa6e9e6f9"
                        },
                        {
                            "name": "트레이닝복",
                            "_id": "bf27b7b8-a0bc-400e-ab7f-3ff7a8c46790",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000841",
                            "cat_id": "50000841",
                            "parentId": "3fcd4b506ad542cbaf6131caa6e9e6f9"
                        },
                        {
                            "name": "점프슈트",
                            "_id": "f091e660-38e2-485f-a773-1a1b0120662b",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50008960",
                            "cat_id": "50008960",
                            "parentId": "3fcd4b506ad542cbaf6131caa6e9e6f9"
                        }
                    ]
                },
                {
                    "name": "여성 언더웨어/잠옷전체보기",
                    "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000168",
                    "cat_id": "50000168",
                    "_id": "e2938b4efabc4c61af4e892a8f38074d",
                    "parentId": "9b56f6852baa42d8bcaee8b0caddf3fb",
                    "childs": [
                        {
                            "name": "브라",
                            "_id": "36d399ba-9b1e-49ec-ba58-82ac5d906a02",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000823",
                            "cat_id": "50000823",
                            "parentId": "e2938b4efabc4c61af4e892a8f38074d"
                        },
                        {
                            "name": "언더웨어소품",
                            "_id": "e56f681e-02f9-4305-896d-ad385b8d5afe",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001454",
                            "cat_id": "50001454",
                            "parentId": "e2938b4efabc4c61af4e892a8f38074d"
                        }
                    ]
                },
                {
                    "name": "남성 언더웨어/잠옷전체보기",
                    "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000170",
                    "cat_id": "50000170",
                    "_id": "14c073c496ef4a51a2d0ee72cb56c44d",
                    "parentId": "9b56f6852baa42d8bcaee8b0caddf3fb",
                    "childs": [
                        {
                            "name": "팬티",
                            "_id": "f7b92f78-ee7b-4fab-9052-f15b322093a3",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000845",
                            "cat_id": "50000845",
                            "parentId": "14c073c496ef4a51a2d0ee72cb56c44d"
                        },
                        {
                            "name": "러닝",
                            "_id": "b54eba54-5fdc-404f-aea5-36cee15fffa4",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000846",
                            "cat_id": "50000846",
                            "parentId": "14c073c496ef4a51a2d0ee72cb56c44d"
                        },
                        {
                            "name": "시즌성내의",
                            "_id": "a1891ddb-9298-45ea-a1e7-a9b796925256",
                            "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001456",
                            "cat_id": "50001456",
                            "parentId": "14c073c496ef4a51a2d0ee72cb56c44d"
                        }
                    ]
                }
            ]
        },
            {
                "name": "디지털/가전",
                "parent_id": "881c48ac698446d48054466636962e30",
                "child": [
                    {
                        "name": "휴대폰전체보기",
                        "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000204",
                        "cat_id": "50000204",
                        "_id": "f2c992c62e0a44b2be36652f234fb0e1",
                        "parentId": "881c48ac698446d48054466636962e30",
                        "childs": [
                            {
                                "name": "휴대폰 케이스",
                                "_id": "b3fa21cf-1621-4b35-bfb5-29e16ed1e78b",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001377",
                                "cat_id": "50001377",
                                "parentId": "f2c992c62e0a44b2be36652f234fb0e1"
                            },
                            {
                                "name": "온수매트",
                                "_id": "ebf44e59-794b-4e2f-9abf-be6369fdf1d2",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50009120",
                                "cat_id": "50009120",
                                "parentId": "f2c992c62e0a44b2be36652f234fb0e1"
                            }
                        ]
                    },
                    {
                        "name": "노트북전체보기",
                        "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000151",
                        "cat_id": "50000151",
                        "_id": "a349ca82ebf8433abb402df243d928a0",
                        "parentId": "881c48ac698446d48054466636962e30",
                        "childs": [
                            {
                                "name": "DSLR 카메라",
                                "_id": "1dc3ef67-798c-4dea-9844-5e77e967994a",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000265",
                                "cat_id": "50000265",
                                "parentId": "a349ca82ebf8433abb402df243d928a0"
                            },
                            {
                                "name": "커피메이커",
                                "_id": "26b5223e-c718-48d0-89df-e3128abc7d4c",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001708",
                                "cat_id": "50001708",
                                "parentId": "a349ca82ebf8433abb402df243d928a0"
                            }
                        ]
                    },
                    {
                        "name": "태블릿PC전체보기",
                        "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000152",
                        "cat_id": "50000152",
                        "_id": "59977f04e84341d0870e649ff495780b",
                        "parentId": "881c48ac698446d48054466636962e30",
                        "childs": [
                            {
                                "name": "TV",
                                "_id": "38d7f013-50f0-45c0-afa3-1df522a1b832",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001395",
                                "cat_id": "50001395",
                                "parentId": "59977f04e84341d0870e649ff495780b"
                            },
                            {
                                "name": "피부케어기기",
                                "_id": "1f4d9e53-13a4-4682-a310-ace2930346c0",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001995",
                                "cat_id": "50001995",
                                "parentId": "59977f04e84341d0870e649ff495780b"
                            }
                        ]
                    },
                    {
                        "name": "PC전체보기",
                        "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000089",
                        "cat_id": "50000089",
                        "_id": "3d7c656d19044e1e83dba14009c7aebc",
                        "parentId": "881c48ac698446d48054466636962e30",
                        "childs": [
                            {
                                "name": "마우스",
                                "_id": "24a570c1-78eb-4487-976b-6af5a34b7075",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001203",
                                "cat_id": "50001203",
                                "parentId": "3d7c656d19044e1e83dba14009c7aebc"
                            },
                            {
                                "name": "PC 게임",
                                "_id": "e840d7fd-69a2-4fb2-b333-6986a20991b3",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001735",
                                "cat_id": "50001735",
                                "parentId": "3d7c656d19044e1e83dba14009c7aebc"
                            }
                        ]
                    },
                    {
                        "name": "모니터전체보기",
                        "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50000153",
                        "cat_id": "50000153",
                        "_id": "57cc6c303fd04aa19796100097418df7",
                        "parentId": "881c48ac698446d48054466636962e30",
                        "childs": [
                            {
                                "name": "CPU",
                                "_id": "a1616fd4-c87a-435c-9e05-81b3504ecabf",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001620",
                                "cat_id": "50001620",
                                "parentId": "57cc6c303fd04aa19796100097418df7"
                            },
                            {
                                "name": "RAM",
                                "_id": "d076fbbd-c33e-42b7-8e43-1501098f3700",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001218",
                                "cat_id": "50001218",
                                "parentId": "57cc6c303fd04aa19796100097418df7"
                            },
                            {
                                "name": "전방/후방 카메라",
                                "_id": "1345ac9b-1abf-4514-9472-8885dedd3cfe",
                                "href": "https://search.shopping.naver.com/category/category.nhn?cat_id=50001191",
                                "cat_id": "50001191",
                                "parentId": "57cc6c303fd04aa19796100097418df7"
                            }
                        ]
                    }
                ]
            }]

if __name__ == '__main__':
    pro = ProductCrawl()










