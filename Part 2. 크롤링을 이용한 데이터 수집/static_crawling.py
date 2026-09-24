import requests as rq

url = 'https://quotes.toscrape.com/'
quote = rq.get(url)

print(quote)

quote.content[:1000]


from bs4 import BeautifulSoup

quote_html = BeautifulSoup(quote.content, 'html.parser')
quote_html.head()

quote_div = quote_html.find_all('div', class_='quote')
quote_div[0]

quote_span = quote_div[0].find_all('span', class_='text')
quote_span

quote_span[0].text

quote_div = quote_html.find_all('div', class_='quote')

[i.find_all('span', class_='text')[0].text for i in quote_div]

quote_div

quote_text = quote_html.select('div.quote > span.text')
quote_text

quote_text_list = [i.text for i in quote_text]
quote_text_list

quote_author = quote_html.select('div.quote > span > small.author')
quote_author_list = [i.text for i in quote_author]
quote_author_list

quote_link = quote_html.select('div.quote > span > a')
quote_link[0]['href']

['http://quotes.toscrape.com' + i['href'] for i in quote_link]


import requests as rq
from bs4 import BeautifulSoup
import time

text_list = []
author_list = []
infor_list = []

for i in range(1,100):

    url = f'https://quotes.toscrape.com/page/{i}/'
    quote = rq.get(url)
    quote_html = BeautifulSoup(quote.content, 'html.parser')

    quote_text = quote_html.select('div.quote > span.text')
    quote_text_list = [i.text for i in quote_text]

    quote_author = quote_html.select('div.quote > span > small.author')
    quote_author_list = [i.text for i in quote_author]

    quote_link = quote_html.select('div.quote > span > a')
    quote_link_list = ['http://quotes.toscrape.com' + i['href'] for i in quote_link]

    if len(quote_text_list) > 0:

        text_list.extend(quote_text_list)
        author_list.extend(quote_author_list)
        infor_list.extend(quote_link_list)
        time.sleep(1)

    else:
        break


text_list
infor_list

import pandas as pd

pd.DataFrame({
    'text': text_list,
    'author': author_list,
    'infor': infor_list
})

import requests as rq
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/news/news_list.naver?mode=LSS2D&section_id=101&section_id2=258'
data = rq.get(url)
html = BeautifulSoup(data.content, "html.parser")
html_select = html.select('dl > dd.articleSubject > a')
html_select[0:3]

html_select[0]['title']

[i['title'] for i in html_select]

import pandas as pd
import requests as rq

url = 'https://en.wikipedia.org/wiki/List_of_countries_by_stock_market_capitalization'
headers = {'User-Agent': 'Mozilla/5.0'}
response = rq.get(url, headers=headers)
tbl = pd.read_html(response.text)

tbl

import requests as rq
from bs4 import BeautifulSoup
import pandas as pd

url = 'https://kind.krx.co.kr/disclosure/todaydisclosure.do?method=searchTodayDisclosureMain&marketType=0'
payload = {
    'method': 'searchTodayDisclosureSub',
    'currentPageSize': '15',
    'pageIndex': '1',
    'orderMode': '0',
    'orderStat': 'D',
    'forward': 'todaydisclosure_sub',
    'chose': 'S',
    'todayFlag': 'N',
    'selDate': '2026-06-16'
}

data = rq.post(url, data=payload)
html = BeautifulSoup(data.content, 'html.parser')
print(html)

html_unicode = html.prettify()
tbl = pd.read_html(html.prettify())
tbl[0].head()

try:
    tbl = pd.read_html(html.prettify())
    print("성공:", len(tbl), "개 테이블")
except Exception as e:
    print("에러:", e)

