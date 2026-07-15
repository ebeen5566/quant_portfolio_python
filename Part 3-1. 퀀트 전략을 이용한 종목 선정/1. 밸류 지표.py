# %%
# 1. 베타 계산하기 
# KOSPI & 키움증권(003940)
import yfinance as yf
import pandas as pd

tickers = ['^KS11', '039490.KS']

all_data = {}
for ticker in tickers:
    all_data[ticker] = yf.download(ticker, 
                                   start = '2020-01-01',
                                   end = '2025-12-31')
    
prices = pd.DataFrame({tic: data['Close'].squeeze() for tic, data in all_data.items()})
ret = prices.pct_change().dropna()

# OLS() : 최소제곱법
import statsmodels.api as sm

ret['intercept'] = 1
reg = sm.OLS(ret[['039490.KS']], ret[['^KS11', 'intercept']]).fit()

reg.summary()
print(reg.params)


# 2. 밸류 전략
# 팩터 데이터 다운로드 (https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
import pandas_datareader.data as web
from pandas_datareader.famafrench import get_available_datasets

datasets = get_available_datasets()
datasets[1:20]

# PBR별 포트폴리오의 수익률
import pandas_datareader.data as web

df_pbr = web.DataReader('Portfolios_Formed_on_BE-ME',
                        'famafrench',
                        start = '1900-01-01')
## key=0 은 시가총액 가중평균 방식의 월간 수익률임
df_pbr[0].tail()

## 단순 수익률(누적)
import matplotlib.pyplot as plt
from matplotlib import cm

plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

df_pbr_vw = df_pbr[0].loc[:, ['Lo 20' ,'Qnt 2', 'Qnt 3', 'Qnt 4', 'Hi 20']]
df_pbr_cum = (1 + df_pbr_vw / 100).cumprod()
df_pbr_cum.plot(figsize=(10,6),
                colormap=cm.jet,
                legend='reverse',
                title='PBR별 포트폴리오의 누적 수익률')
plt.show()

## 로그 수익률
import numpy as np

df_pbr_cum = np.log(1+df_pbr_vw/100).cumsum()
df_pbr_cum.plot(figsize=(10,6),
                colormap=cm.jet,
                legend='reverse',
                title='PBR별 포트폴리오의 누적 수익률')
plt.show()

# PBR별 포트폴리오 성과 비교(기하 수익률, 산술 수익률, 변동성, 샤프지수 - 연율화)
# %%
import pandas as pd

def factor_stat(df):

    n = len(df)

    ret_ari = (df / 100).mean(axis=0) * 12
    ret_geo = (1 + df / 100).prod()**(12 / n) - 1
    vol = (df / 100).std(axis=0) * np.sqrt(12)
    sharp = ret_ari / vol

    stat = pd.DataFrame(
        [ret_ari, ret_geo, vol, sharp],
        index=['연율화 수익률(산술)', '연율화 수익률(기하)', '연율화 변동성', '샤프지수']).round(4)
    
    stat.iloc[0:3, ] = stat.iloc[0:3, ] * 100

    return stat

# %%
factor_stat(df_pbr_vw)

# PER별 포트폴리오 누적 수익률
# %%
df_per = web.DataReader('Portfolios_Formed_on_E-P',
                        'famafrench',
                        start='1900-01-01')
df_per_vw = df_per[0].loc[:, ['Lo 20', 'Qnt 2', 'Qnt 3', 'Qnt 4', 'Hi 20']]
df_per_cum = np.log(1 + df_per_vw / 100).cumsum()
df_per_cum.plot(figsize=(10,6),
                colormap=cm.jet,
                legend='reverse',
                title='PER별 포트폴리오의 누적 수익률')
plt.show()

# %%
# PCR별 포트폴리오 누적 수익률
# %%
df_pcr = web.DataReader('Portfolios_Formed_on_CF-P',
                        'famafrench',
                        start='1900-01-01')
df_pcr_vw = df_per[0].loc[:, ['Lo 20', 'Qnt 2', 'Qnt 3', 'Qnt 4', 'Hi 20']]
df_pcr_cum = np.log(1 + df_pcr_vw / 100).cumsum()
df_pcr_cum.plot(figsize=(10,6),
                colormap=cm.jet,
                legend='reverse',
                title='PCR별 포트폴리오의 누적 수익률')
plt.show()

# %%
# 밸류 포트폴리오 구하기 - 국내 주식
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')

ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
    and 종목구분 = '보통주';
""", con=engine)

value_list = pd.read_sql("""
select * from kor_value
where 기준일 = (select max(기준일) from kor_value);
""", con=engine)

engine.dispose()
# %%
value_list.loc[value_list['값'] <= 0, '값'] = np.nan
value_pivot = value_list.pivot(index='종목코드', columns='지표', values='값')
data_bind = ticker_list[['종목코드', '종목명']].merge(value_pivot,
                                                    how='left',
                                                    on='종목코드')
data_bind.head()

## 저PER, 저PBR주 찾기
# %%
value_rank = data_bind[['PER', 'PBR']].rank(axis=0)
value_sum = value_rank.sum(axis=1, skipna=False).rank()
data_bind.loc[value_sum <= 20, ['종목코드', '종목명', 'PER', 'PBR']]

## 여러 지표 결합하기 - PER, PBR, PCR, PSR, DY
# %%
### 지표별 상관관계
import matplotlib.pyplot as plt
import seaborn as sns

value_list_copy = data_bind.copy()
value_list_copy['DY'] = 1 / value_list_copy['DY']
value_list_copy = value_list_copy[['PER', 'PBR', 'PCR', 'PSR', 'DY']]
value_rank_all = value_list_copy.rank(axis=0)
mask = np.triu(value_rank_all.corr())

mask = np.triu(value_rank_all.corr())
fig, ax = plt.subplots(figsize=(10,6))
sns.heatmap(value_rank_all.corr(),
            annot=True,
            mask=mask,
            annot_kws={"size":16},
            vmin=1,
            center=0.5,
            cmap='coolwarm',
            square=True)
ax.invert_yaxis()
plt.show()

### 5개 지표가 모두 낮은 20개 종목 산출
# %%
value_sum_all = value_rank_all.sum(axis=1, skipna=False).rank()
data_bind.loc[value_sum_all <= 20]

# 3. 모멘텀 전략
# %%
