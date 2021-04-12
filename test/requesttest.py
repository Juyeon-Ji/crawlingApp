import requests
import uuid
import re
import json
from bs4 import BeautifulSoup
from lxml import html, etree
from lxml.html import HtmlElement

from common.util import Utils

def productlist():
    # key="da302a3c8bfb3783ed2d6b98c8be4f63"
    # keyword = "test"
    # url = "https://openapi.11st.co.kr/openapi/OpenApiService.tmall?key="+key+"&apiCode=ProductSearch&keyword=" + keyword
    # categoryURL = 'http://openapi.11st.co.kr/openapi/OpenApiService.tmall?key=[{0}]&apiCode=CategoryInfo&categoryCode=1'.format(key)
    # URL = "https://search.shopping.naver.com/search/category?catId=50003550&frm=NVSHPRC&maxPrice=10000&minPrice=3500&origQuery&pagingIndex=2&pagingSize=800&productSet=model&query&sort=rel&timestamp=&viewType=list"
    URL = "https://search.shopping.naver.com/search/category?catId=50003822&frm=NVSHMDL&maxPrice=3500&minPrice=1000&origQuery&pagingIndex=1&pagingSize=40&productSet=model&query&sort=rel&timestamp=&viewType=list"
    # 필요없음
    headers = {'Content-Type': 'application/json;'}

    req = requests.get(URL, headers)

    html = req.text
    print(html)

    soup = BeautifulSoup(html, 'html.parser')  # html.parser를 사용해서 soup에 넣겠다

    json_data = soup.find('script', text=re.compile('application/json'))


def sub_category(element: HtmlElement, root_path: str):

    ul_tag: HtmlElement = element.find('ul')

    if ul_tag is not None:
        li_tags = ul_tag.findall('li')

        li: HtmlElement
        for li in li_tags:
            try:
                li_a_tag = li.find('a')
                if li_a_tag is not None:
                    href = li_a_tag.get('href')
                    text = li_a_tag.text
                    paths = Utils.join_path('#', root_path, text)
                    div_tag = li.find('div')
                    if div_tag is not None:
                        sub_category(div_tag, paths)

                    if li.find('ul') is not None:
                        sub_category(li, paths)
            except Exception as e:
                print('')


def category(i):
    URL = "https://search.shopping.naver.com/category/category/" + str(i)

    headers = {'Content-Type': 'application/json;'}

    req = requests.get(URL, headers)

    content = req.content

    # tree: HtmlElement = etree.fromstring(content)
    tree: HtmlElement = html.fromstring(content)
    header_xpath = '//*[@id="__next"]/div/div[2]/h2'
    header = tree.xpath(header_xpath)[0].text

    xpath = '//*[@id="__next"]/div/div[2]/div/div'
    elements: [HtmlElement] = tree.xpath(xpath)

    element: HtmlElement
    for i, element in enumerate(elements):
        print(i)
        try:
            if element.find('div') is not None:
                a_tag: HtmlElement = element[0].find('h3').find('a')
                href = a_tag.get('href')
                _cid = Utils.separate_right(href, "category?catId=")
                h3_tag = a_tag.find('strong').text
                paths = Utils.join_path('#', header, h3_tag)
                sub_category(element[0], paths)

        except Exception as e:
            print('')
if __name__ == '__main__':

    for i in range(50000000,50000000 + 11):
        category(i)

    pass