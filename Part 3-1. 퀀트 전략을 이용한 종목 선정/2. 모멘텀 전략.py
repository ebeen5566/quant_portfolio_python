# 1. 모멘텀별 포트폴리오의 수익률
import pandas_datareader.data as web
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

df_mom = web.DataReader('10_Portfolios_Prior_12_2',
                        'famafrench',
                        start='1900-01-01')
df_mom_vw = df_mom[0]
df_mom_cum = np.log(1 + df_mom_vw / 100).cumsum()

plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

df_mom_cum.plot(figsize=(10,6),
                colormap=cm.jet,
                legend='reverse',
                title='모멘텀별 포트폴리오의 누적 수익률')
plt.show()

## 포트폴리오별 통계값 확인
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

factor_stat(df_mom_vw)

# 2. 모멘텀 포트폴리오 구하기
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')

ticker_list = pd.read_sql(
"""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
    and 종목구분 = '보통주';
""", con=engine)

price_list = pd.read_sql(
"""
select 날짜, 종가, 종목코드
from kor_price
where 날짜 >= (select (select max(날짜) from kor_price) - interval 1 year);
""", con=engine)

engine.dispose()

price_list.head()

price_pivot = price_list.pivot(index='날짜', columns='종목코드', values='종가')
price_pivot.iloc[0:5, 0:5]

ret_list = pd.DataFrame(data=(price_pivot.iloc[-1] / price_pivot.iloc[0]) - 1, 
                        columns=['return'])
data_bind = ticker_list[['종목코드', '종목명']].merge(ret_list, how='left', on='종목코드')
data_bind.head()

momentum_rank = data_bind['return'].rank(axis=0, ascending=False)
data_bind[momentum_rank <= 20]

price_momentum = price_list[price_list['종목코드'].isin(
    data_bind.loc[momentum_rank <= 20, '종목코드'])]

import matplotlib.pyplot as plt
import seaborn as sns

plt.rc('font', family='Malgun Gothic')
g = sns.relplot(data=price_momentum,
                x='날짜',
                y='종가',
                col='종목코드',
                col_wrap=5,
                kind='line',
                facet_kws={
                    'sharey' : False,
                    'sharex' : True
                })
g.set(xticklabels=[])
g.set(xlabel=None)
g.set(ylabel=None)
g.fig.set_figwidth(15)
g.fig.set_figheight(8)
plt.subplots_adjust(wspace=0.5, hspace=0.2)
plt.show()


# 3. K-Ratio : (누적 수익률의 기울기 / 표준 오차)
import statsmodels.api as sm
import numpy as np

ret = price_pivot.pct_change().iloc[1:]
ret_cum = np.log(1 + ret).cumsum()

x = np.array(range(len(ret)))
y = ret_cum.iloc[:, 0].values

reg = sm.OLS(y, x).fit()
reg.summary()
print(reg.params, reg.bse, (reg.params / reg.bse))

## 전종목 K-Ratio 산출
x = np.array(range(len(ret)))
k_ratio = {}

for i in range(0, len(ticker_list)):

    ticker = data_bind.loc[i, '종목코드']

    try:
        y = ret_cum.loc[: , price_pivot.columns == ticker]
        reg = sm.OLS(y, x).fit()
        res = float(reg.params / reg.bse)
    except:
        res = np.nan

    k_ratio[ticker] = res

k_ratio_bind = pd.DataFrame.from_dict(k_ratio, orient='index').reset_index()
k_ratio_bind.columns = ['종목코드', 'K_ratio']

k_ratio_bind.head()

### K-Ratio 높은 종목 산출
data_bind = data_bind.merge(k_ratio_bind, how='left', on='종목코드')
k_ratio_rank = data_bind['K_ratio'].rank(axis=0, ascending=False)
data_bind[k_ratio_rank <= 20]

k_ratio_momentum = price_list[price_list['종목코드'].isin(
    data_bind.loc[k_ratio_rank <= 20, '종목코드'])]

plt.rc('font', family='Malgun Gothic')
g = sns.relplot(data=k_ratio_momentum,
                x='날짜',
                y='종가',
                col='종목코드',
                col_wrap=5,
                kind='line',
                facet_kws={
                    'sharex':False,
                    'sharey':True
                })
g.set(xticklabels=[])
g.set(xlabel=None)
g.set(ylabel=None)
g.fig.set_figwidth(15)
g.fig.set_figheight(8)
plt.subplots_adjust(wspace=0.5, hspace=0.2)
plt.show()

