import requests
import re
import json
from bs4 import BeautifulSoup  # BeautifulSoup import

def crawlingtest(i):


    except_data_count: int = 0

    URL = "https://search.shopping.naver.com/search/category?catId=50007588&frm=NVSHMDL&origQuery&pagingIndex="+str(i)+"&pagingSize=20&productSet=model&query&sort=rel&timestamp=&viewType=list"

    headers = {'Content-Type': 'application/json;'}

    req = requests.get(URL, headers)

    html = req.text

    soup = BeautifulSoup(html, 'html.parser')  # html.parser를 사용해서 soup에 넣겠다

    json_data = soup.find('script', text=re.compile('application/json'))

    data_dict = json.loads(str(json_data.contents[0]))

    product_info:dict = data_dict['props']['pageProps']['initialState']['products']
    product_list:dict = product_info['list']
    product_total_count: dict = product_info['total']

    products_data: list = []
    print("총 상품 수: " + str(product_total_count))
    print("수집 시작 데이터 수: " + str(len(product_list)))
    for product in product_list:
        product_data: dict = {}

        product_item = product['item']
        if( "adId" not in product_item):
            product_data['id'] = product_item['id']
            product_data['imageUrl'] = product_item['imageUrl']
            product_data['productTitle'] = product_item['productTitle']

            product_data['option'] = {}
            if(product_item['attributeValue']):
                product_data['productOptionKey'] = product_item['attributeValue'].split('|')
                product_data['productOptionValue'] = product_item['characterValue'].split('|')

                product_data['option'] = dict(zip(product_data['productOptionKey'], product_data['productOptionValue']))

            products_data.append(product_data)
        else:
            except_data_count += 1
            print(str(except_data_count) + ".광고 데이터 제외")

    print("수집 완료 데이터 수: " + str(len(products_data)))
    print("수집 제외된 데이터 수: " + str(except_data_count))

    if len(product_list) != len(products_data) + except_data_count:
        print("!!!! EXCEPTION: 데이터 수 확인이 필요 합니다.")

    print(products_data)
if __name__ == "__main__":
    for i in range(1, 3):
	    crawlingtest(i)