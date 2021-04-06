import requests
import uuid

print(uuid.uuid4())

key="da302a3c8bfb3783ed2d6b98c8be4f63"
keyword = "test"
url = "https://openapi.11st.co.kr/openapi/OpenApiService.tmall?key="+key+"&apiCode=ProductSearch&keyword=" + keyword
categoryURL = 'http://openapi.11st.co.kr/openapi/OpenApiService.tmall?key=[{0}]&apiCode=CategoryInfo&categoryCode=1'.format(key)
req = requests.get(categoryURL)

html = req.text

print(html)

