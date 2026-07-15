# %%
# 최근 영업일 기준 데이터 받기 - 네이버페이증권/국내증시/증시자금동향
import requests as rq
from bs4 import BeautifulSoup

url = 'https://finance.naver.com/sise/sise_deposit.naver'
data = rq.get(url)
data_html = BeautifulSoup(data.content)
parse_day = data_html.select_one(
    'div.subtop_sise_graph2 > ul.subtop_chart_note > li > span.tah').text

print(parse_day)

import re

biz_day = re.findall('[0-9]+', parse_day)
biz_day = ''.join(biz_day)
print(biz_day)

# %%
# 한국거래소의 업종분류 현황 및 개별지표 크롤링 - 20251227 이후로 웹스크래핑 불가능해짐(서버 과부화 이슈)
# pykrx 와 FinanceDataReader 결합해서 KRX Data Marketplace 업종분류 현황(12025) 화면 최대한 유사하게 만들어보고자 함
# https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201
# 아무리 해봐도 답이 없어서 csv 파일 다운로드해서 데이터프레임 제작함

import pandas as pd

df_kospi = pd.read_csv('data_kospi_20260619.csv', encoding='cp949')
df_kospi.head()
len(df_kospi['업종명'].unique().tolist())

df_kosdaq = pd.read_csv('data_kosdaq_20260619.csv', encoding='cp949')
df_kosdaq.head()

krx_sector = pd.concat([df_kospi, df_kosdaq]).reset_index(drop=True)
krx_sector['종목명'] = krx_sector['종목명'].str.strip()
krx_sector['기준일'] = '20260617'

krx_sector.head()

krx_ind = pd.read_csv('per_pbr_div_20260619.csv', encoding='cp949')
krx_ind['종목명'] = krx_ind['종목명'].str.strip()
krx_ind['기준일'] = '20260617'
krx_ind.head()

# 데이터 정리하기
diff = list(set(krx_sector['종목명']).symmetric_difference(set(krx_ind['종목명'])))
print(diff)

kor_ticker = pd.merge(krx_sector,
                      krx_ind,
                      on=krx_sector.columns.intersection(
                          krx_ind.columns).tolist(),
                          how = 'outer')

kor_ticker.head()

print(kor_ticker[kor_ticker['종목명'].str.contains('스팩|제[0-9]+호')]['종목명'].values)
print(kor_ticker[kor_ticker['종목명'].str[-1:] != '0']['종목명'].values)
print(kor_ticker[kor_ticker['종목명'].str.endswith('리츠')]['종목명'].values)

import numpy as np

kor_ticker['종목구분'] = np.where(kor_ticker['종목명'].str.contains('스팩|제[0-9]+호'), '스팩',
                              np.where(kor_ticker['종목코드'].str[-1:] != '0', '우선주',
                                       np.where(kor_ticker['종목명'].str.endswith('리츠'), '리츠',
                                                np.where(kor_ticker['종목명'].isin(diff), '기타',
                                                         '보통주'))))

kor_ticker = kor_ticker.reset_index(drop=True)
kor_ticker.columns = kor_ticker.columns.str.replace(' ','')
kor_ticker = kor_ticker[['종목코드', '종목명', '시장구분', '종가', '시가총액',
                         '기준일', 'EPS', '선행EPS', 'BPS', '주당배당금', '종목구분']]
kor_ticker = kor_ticker.replace({np.nan: None})
kor_ticker['기준일'] = pd.to_datetime(kor_ticker['기준일'])

kor_ticker.head()

# %%
import pymysql

con = pymysql.connect(
    user = 'root',
    passwd = '',
    host='127.0.0.1',
    db='stock_db',
    charset='utf8'
)

mycursor = con.cursor()
query =f"""
    insert into kor_ticker (종목코드, 종목명, 시장구분, 종가, 시가총액, 기준일, EPS, 선행EPS, BPS, 주당배당금, 종목구분)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    종목명=new.종목명, 시장구분=new.시장구분, 종가=new.종가, 시가총액=new.시가총액, EPS=new.EPS, 선행EPS=new.선행EPS, BPS=new.BPS,
    주당배당금=new.주당배당금, 종목구분=new.종목구분;
"""

args = kor_ticker.values.tolist()
mycursor.executemany(query, args)
con.commit()
con.close()

# %%
# WICS 기준 섹터 정보 크롤링

import json
import requests as rq
import pandas as pd

biz_day = '20260617'

url=f'''https://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={biz_day}&sec_cd=G10'''
data = rq.get(url).json()

type(data)

print(data.keys())
data['list'][0]
data['sector']

data_pd = pd.json_normalize(data['list'])
data_pd.head()

# %%
import time
import json
import requests as rq
import pandas as pd
from tqdm import tqdm

sector_code = [
    'G25', 'G35', 'G50', 'G40', 'G10', 'G20', 'G55', 'G30', 'G15', 'G45'
]

data_sector = []

for i in tqdm(sector_code):
    url = f'''https://www.wiseindex.com/Index/GetIndexComponets?ceil_yn=0&dt={biz_day}&sec_cd={i}'''
    data = rq.get(url).json()
    data_pd = pd.json_normalize(data['list'])

    data_sector.append(data_pd)

    time.sleep(2)

data_sector

kor_sector = pd.concat(data_sector, axis = 0)
kor_sector = kor_sector[['IDX_CD', 'CMP_CD', 'CMP_KOR', 'SEC_NM_KOR']]
kor_sector['기준일'] = biz_day
kor_sector['기준일'] = pd.to_datetime(kor_sector['기준일'])

# %%
import pymysql

con = pymysql.connect(
    user='root',
    passwd='',
    host='127.0.0.1',
    db='stock_db',
    charset='utf8'
)

mycursor = con.cursor()
query = f"""
    insert into kor_sector (IDX_CD, CMP_CD, CMP_KOR, SEC_NM_KOR, 기준일)
    values (%s, %s, %s, %s, %s) as new
    on duplicate key update
    IDX_CD = new.IDX_CD, CMP_CD = new.CMP_CD, CMP_KOR = new.CMP_KOR, SEC_NM_KOR = new.SEC_NM_KOR, 기준일 = new.기준일 
"""
args = kor_sector.values.tolist()

mycursor.executemany(query, args)
con.commit()
con.close()

# %%
# 수정주가 크롤링
## 티커 데이터 불러오기
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')
query = """
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
    and 종목구분 = '보통주';
"""
ticker_list = pd.read_sql(query, con=engine)
engine.dispose()

ticker_list.head()

## 주가 데이터 페이지 크롤링하기
from dateutil.relativedelta import relativedelta
import requests as rq
from io import BytesIO
from datetime import date

i = 0
ticker = ticker_list['종목코드'][i]
fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d")
to = (date.today()).strftime("%Y%m%d")

url = f'''https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={ticker}&requestType=1&startTime={fr}&endTime={to}&timeframe=day'''

data = rq.get(url).content
data_price = pd.read_csv(BytesIO(data))

data_price.head()

# %%
## 추가 클렌징 작업
import re

price = data_price.iloc[:, 0:6]
price.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
price = price.dropna()
price['날짜'] = price['날짜'].str.extract('(\d+)')
price['날짜'] = pd.to_datetime(price['날짜'])
price['종목코드'] = ticker

price.head()

# %%
## 전 종목 주가 크롤링
import pymysql
from sqlalchemy import create_engine
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import requests as rq
import time
from tqdm import tqdm
from io import BytesIO

# DB 연결
engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='root', 
                      passwd='',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')
mycursor = con.cursor()

# 티커 리스트 불러오기
ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
      and 종목구분 = '보통주';
""", con=engine)

# DB 저장 쿼리
query = """
    insert into kor_price (날짜, 시가, 고가, 저가, 종가, 거래량, 종목코드)
    values (%s,%s,%s,%s,%s,%s,%s) as new
    on duplicate key update
    시가=new.시가, 고가=new.고가, 저가=new.저가, 
    종가=new.종가, 거래량=new.거래량;
"""

# 오류 발생 시 저장할 리스트 생성
error_list = []

# 전 종목 주가 다운로드 및 저장
for i in tqdm(range(0, len(ticker_list))):

    # 티커 선택
    ticker = ticker_list['종목코드'][i]

    # 시작일과 종료일
    fr = (date.today() + relativedelta(years=-5)).strftime("%Y%m%d")
    to = (date.today()).strftime("%Y%m%d")

    # 오류 발생 시 이를 무시하고 다음 루프로 진행
    try:

        # url 생성
        url = f'''https://m.stock.naver.com/front-api/external/chart/domestic/info?symbol={ticker}&requestType=1&startTime={fr}&endTime={to}&timeframe=day'''

        # 데이터 다운로드
        data = rq.get(url).content
        data_price = pd.read_csv(BytesIO(data))

        # 데이터 클렌징
        price = data_price.iloc[:,0:6]
        price.columns = ['날짜', '시가', '고가', '저가', '종가', '거래량']
        price = price.dropna()
        price['날짜'] = price['날짜'].str.extract('(\d+)')
        price['날짜'] = pd.to_datetime(price['날짜'])
        price['종목코드'] = ticker

        # 주가 데이터를 DB에 저장
        args = price.values.tolist()
        mycursor.executemany(query, args)
        con.commit()

    except:

        # 오류 발생 시 error_list에 티커 저장하고 넘어가기
        print(ticker)
        error_list.append(ticker)

    # 타입슬립 적용
    time.sleep(2)

# DB 연결 종료
engine.dispose()
con.close()


# %%
# 재무제표 크롤링

from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')
query = """
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
and 종목구분 = '보통주';
"""

ticker_list = pd.read_sql(query, con=engine)
engine.dispose()

i = 0
ticker = ticker_list['종목코드'][i]

url = f'https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{ticker}'
data = pd.read_html(url, displayed_only=False)

[item.head(3) for item in data]

# %%
print(
    data[0].columns.tolist(), '\n',
    data[2].columns.tolist(), '\n',
    data[4].columns.tolist()
)
# %%
data_fs_y = pd.concat(
    [data[0].iloc[:,~data[0].columns.str.contains('전년동기')], data[2], data[4]])
data_fs_y = data_fs_y.rename(columns={data_fs_y.columns[0]: "계정"})

data_fs_y.head()

# %%
import requests as rq
from bs4 import BeautifulSoup
import re

page_data = rq.get(url)
page_data_html = BeautifulSoup(page_data.content, 'html.parser')

fiscal_data = page_data_html.select('div.corp_group1 > h2')
fiscal_data_text = fiscal_data[1].text
fiscal_data_text = re.findall('[0-9]+', fiscal_data_text)

data_fs_y = data_fs_y.loc[:, (data_fs_y.columns == '계정') | 
                          (data_fs_y.columns.str[-2:].isin(fiscal_data_text))]
data_fs_y[data_fs_y.loc[:, ~data_fs_y.columns.isin(['계정'])].isna().all(axis=1)].head()
data_fs_y['계정'].value_counts(ascending=False)

def clean_fs(df, ticker, frequency):

    df = df[~df.loc[:, ~df.columns.isin(['계정'])].isna().all(axis=1)]
    df = df.drop_duplicates(['계정'], keep='first')
    df = pd.melt(df, id_vars='계정', var_name='기준일', value_name='값')
    df = df[~pd.isnull(df['값'])]
    df['계정'] = df['계정'].replace({'계산에 참여한 계정 펼치기': ''}, regex=True)
    df['기준일'] = pd.to_datetime(df['기준일'], format='%Y/%m') + pd.tseries.offsets.MonthEnd()
    df['종목코드'] = ticker
    df['공시구분'] = frequency

    return df

data_fs_y_clean = clean_fs(data_fs_y, ticker, 'y')

# %%
# 분기 데이터 
data_fs_q = pd.concat(
    [data[1].iloc[:, ~data[1].columns.str.contains('전년동기')], data[3], data[5]])
data_fs_q = data_fs_q.rename(columns={data_fs_q.columns[0]: '계정'})
data_fs_q_clean = clean_fs(data_fs_q, ticker, 'q')
data_fs_bind = pd.concat([data_fs_y_clean, data_fs_q_clean])

# %%
# 전 종목 재무제표 크롤링
## 패키지 불러오기
import pymysql
from sqlalchemy import create_engine
import pandas as pd
import requests as rq
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
import time

## DB 연결
engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='root',
                      passwd='',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')
mycursor = con.cursor()

## 티커 리스트 불러오기
ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
    and 종목구분 = '보통주';
""", con=engine)

## DB 저장 쿼리
query = """
    insert into kor_fs (계정, 기준일, 값, 종목코드, 공시구분)
    values (%s,%s,%s,%s,%s) as new
    on duplicate key update
    값 = new.값
"""

## 오류 발생 시 저장할 리스트 생성
error_list = []

## 재무제표 클렌징 함수
def clean_fs(df, ticker, frequency):

    df = df[~df.loc[:, ~df.columns.isin(['계정'])].isna().all(axis=1)]
    df = df.drop_duplicates(['계정'], keep='first')
    df = pd.melt(df, id_vars='계정', var_name='기준일', value_name='값')
    df = df[~pd.isnull(df['값'])]
    df['계정'] = df['계정'].replace({'계산에 참여한 계정 펼치기': ''}, regex=True)
    df['기준일'] = pd.to_datetime(df['기준일'], format='%Y/%m') + pd.tseries.offsets.MonthEnd()
    df['종목코드'] = ticker
    df['공시구분'] = frequency

    return df

## for loop
for i in tqdm(range(0, len(ticker_list))):

    # 티커 선택
    ticker = ticker_list['종목코드'][i]

    # 오류 발생 시 이를 무시하고 다음 루프로 진행
    try:

        # url 생성
        url = f'https://comp.fnguide.com/SVO2/ASP/SVD_Finance.asp?pGB=1&gicode=A{ticker}'

        # 데이터 받아오기
        data = pd.read_html(url, displayed_only=False)

        # 연간 데이터
        data_fs_y = pd.concat(
        [data[0].iloc[:,~data[0].columns.str.contains('전년동기')], data[2], data[4]])
        data_fs_y = data_fs_y.rename(columns={data_fs_y.columns[0]: "계정"})

        # 결산년 찾기
        page_data = rq.get(url)
        page_data_html = BeautifulSoup(page_data.content, 'html.parser')

        fiscal_data = page_data_html.select('div.corp_group1 > h2')
        fiscal_data_text = fiscal_data[1].text
        fiscal_data_text = re.findall('[0-9]+', fiscal_data_text)

        # 결산년에 해당하는 계정만 남기기
        data_fs_y = data_fs_y.loc[:, (data_fs_y.columns == '계정') | 
                          (data_fs_y.columns.str[-2:].isin(fiscal_data_text))]

        # 클렌징
        data_fs_y_clean = clean_fs(data_fs_y, ticker, 'y')

        # 분기 데이터
        data_fs_q = pd.concat(
        [data[1].iloc[:, ~data[1].columns.str.contains('전년동기')], data[3], data[5]])
        data_fs_q = data_fs_q.rename(columns={data_fs_q.columns[0]: '계정'})
        data_fs_q_clean = clean_fs(data_fs_q, ticker, 'q')

        # 2개 합치기
        data_fs_bind = pd.concat([data_fs_y_clean, data_fs_q_clean])

        # 재무제표 데이터를 DB에 저장
        args = data_fs_bind.values.tolist()
        mycursor.executemany(query, args)
        con.commit()

    except:

        # 오류 발생 시 해당 종목명을 저장하고 다음 루프로 이동
        print(ticker)
        error_list.append(ticker)

    # 타임슬립 적용
    time.sleep(2)

# DB 연결 종료
engine.dispose()
con.close()

# 가치지표 계산
## 패키지 불러오기
from sqlalchemy import create_engine
import pandas as pd

## DB 연결
engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')

## 티커 리스트
ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
                          and 종목구분 = "보통주";                      
""", con=engine)


# ## E.G. 삼성전자 분기 재무제표
# sample_fs = pd.read_sql("""
# select * from kor_fs
# where 공시구분 = 'q'
# and 종목코드 = '005930'
# and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
# """, con=engine)

# engine.dispose()

# sample_fs = sample_fs.sort_values(['종목코드', '계정', '기준일'])
# sample_fs.head()
# sample_fs['ttm'] = sample_fs.groupby(
#     ['종목코드', '계정'], as_index=False)['값'].rolling(window=4, min_periods=4).sum()['값']

# # %%
# import numpy as np

# sample_fs['ttm'] = np.where(sample_fs['계정'] == '자본',
#                              sample_fs['ttm'] / 4, sample_fs['ttm'])
# sample_fs = sample_fs.groupby(['계정', '종목코드']).tail(1)

# sample_fs.head()
# # %%
# sample_fs_merge = sample_fs[['계정', '종목코드', 'ttm']].merge(
#     ticker_list[['종목코드', '시가총액', '기준일']], on='종목코드')
# sample_fs_merge['시가총액'] = sample_fs_merge['시가총액']/100000000

# sample_fs_merge.head()
# # %%
# sample_fs_merge['value'] = sample_fs_merge['시가총액'] / sample_fs_merge['ttm']
# sample_fs_merge['지표'] = np.where(
#     sample_fs_merge['계정'] == '매출액', 'PSR',
#     np.where(
#         sample_fs_merge['계정'] == '영업활동으로인한현금흐름', 'PCR',
#         np.where(sample_fs_merge['계정'] == '자본', 'PBR',
#                 np.where(sample_fs_merge['계정'] == '당기순이익', 'PER', None))))

# sample_fs_merge

# ticker_list_sample = ticker_list[ticker_list['종목코드'] == '005930'].copy()
# ticker_list_sample['DY'] = ticker_list_sample['주당배당금'] / ticker_list_sample['종가']

# ticker_list_sample.head()


# %%
# 전 종목 가치지표 계산
## 패키지 불러오기
import pymysql
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

## DB 연결
engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')
con = pymysql.connect(user='root',
                      passwd='',
                      host='127.0.0.1',
                      db='stock_db',
                      charset='utf8')
mycursor = con.cursor()

## 분기 재무제표 불러오기
kor_fs = pd.read_sql("""
select * from kor_fs
where 공시구분 = 'q'
and 계정 in ('당기순이익', '자본', '영업활동으로인한현금흐름', '매출액');
""", con=engine)

engine.dispose()

## ttm 구하기
kor_fs = kor_fs.sort_values(['종목코드', '계정', '기준일'])
kor_fs['ttm'] = kor_fs.groupby(['종목코드', '계정'], as_index=False)['값'].rolling(
    window=4, min_periods=4).sum()['값']

## 자본은 평균 구하기
kor_fs['ttm'] = np.where(kor_fs['계정'] == '자본', kor_fs['ttm'] / 4, kor_fs['ttm'])
kor_fs = kor_fs.groupby(['계정', '종목코드']).tail(1)

## 합치기
kor_fs_merge = kor_fs[['계정', '종목코드', 'ttm']].merge(ticker_list[['종목코드', '시가총액', '기준일']],
                                                   on='종목코드')
kor_fs_merge['시가총액'] = kor_fs_merge['시가총액'] / 100000000

kor_fs_merge['value'] = kor_fs_merge['시가총액'] / kor_fs_merge['ttm']
kor_fs_merge['value'] = kor_fs_merge['value'].round(4)
kor_fs_merge['지표'] = np.where(
    kor_fs_merge['계정'] == '매출액', 'PSR',
    np.where(
        kor_fs_merge['계정'] == '영업활동으로인한현금흐름', 'PCR',
        np.where(kor_fs_merge['계정'] == '자본', 'PBR',
                np.where(kor_fs_merge['계정'] == '당기순이익', 'PER', None))))

kor_fs_merge.rename(columns={'value':'값'}, inplace=True)
kor_fs_merge = kor_fs_merge[['종목코드', '기준일', '지표', '값']]
kor_fs_merge = kor_fs_merge.replace([np.inf, -np.inf, np.nan], None)

kor_fs_merge.head(4)

# %%
query = """
    insert into kor_value (종목코드, 기준일, 지표, 값)
    values (%s,%s,%s,%s) as new
    on duplicate key update
    값 = new.값
"""

args_fs = kor_fs_merge.values.tolist()
mycursor.executemany(query, args_fs)
con.commit()

ticker_list['값'] = ticker_list['주당배당금'] / ticker_list['종가']
ticker_list['값'] = ticker_list['값'].round(4)
ticker_list['지표'] = 'DY'
dy_list = ticker_list[['종목코드', '기준일', '지표', '값']]
dy_list = dy_list.replace([np.inf, -np.inf, np.nan], None)
dy_list = dy_list[dy_list['값'] != 0]

args_dy = dy_list.values.tolist()
mycursor.executemany(query, args_dy)
con.commit()

engine.dispose()
con.close()
# %%
