import unittest
import requests
from lxml import html, etree
from lxml.html import HtmlElement


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        # 패션 의류 카테고리로 테스트 진행
        url = "https://search.shopping.naver.com/category/category/50000000"

        self.request = requests.get(url)

    def tearDown(self) -> None:
        self.request.close()
        pass

    def test_response_content_root_name(self):
        pass

    def test_something(self):
        self.assertEqual(True, False)


if __name__ == '__main__':
    unittest.main()
