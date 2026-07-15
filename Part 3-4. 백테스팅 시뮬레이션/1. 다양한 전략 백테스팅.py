# 1 .bt 패키지
# 1. 데이터의 수집 -> 2. 전략의 정의 -> 3. 데이터를 이용한 전략의 백테스트 -> 4. 결과에 대한 평가
# %%
## 1. 데이터의 수집
from sqlalchemy import create_engine
import pandas as pd

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')
price = pd.read_sql("""
select * from sample_etf;
""", con=engine)
price = price.set_index(['Date'])
engine.dispose()

price.tail()

# %%
## 2. 전략의 정의
import bt

### 전체 자산 동일비중, 매월 말 리밸런싱
strategy = bt.Strategy('Asset_EW', [
    bt.algos.SelectAll(),
    bt.algos.WeighEqually(),
    bt.algos.RunMonthly(),
    bt.algos.Rebalance()
])

# %%
## 3. 전략의 백테스트
data = price.dropna()

backtest = bt.Backtest(strategy, data)

result = bt.run(backtest)

# %%
## 4. 결과 평가
result.prices

# %%
result.prices.to_returns()

# %%
import matplotlib.pyplot as plt
%matplotlib inline

result.plot(figsize=(10,6), legend=False)
plt.show()

# %%
result.get_security_weights().tail()

# %%
from matplotlib import cm

ax= result.get_security_weights().plot.area(figsize=(10,6),
                                            ylim=[0,1],
                                            legend=False,
                                            colormap=cm.jet)
handles, labels = ax.get_legend_handles_labels()
plt.margins(0,0)
plt.legend(reversed(handles),
           reversed(labels),
           loc='lower right',
           bbox_to_anchor=(1.15, 0))
plt.show()

# %%
result.display()

# %%
# 2. 정적 자산배분: 올웨더 포트폴리오
import bt
import matplotlib.pyplot as plt
%matplotlib inline

data = price[['SPY', 'TLT', 'IEF', 'GLD', 'DBC']].dropna()

aw = bt.Strategy('All Weather', [
    bt.algos.SelectAll(),
    bt.algos.WeighSpecified(SPY=0.3, TLT=0.4, IEF=0.15, GLD=0.075, DBC=0.075),
    bt.algos.RunQuarterly(),
    bt.algos.Rebalance()
])
aw_backtest = bt.Backtest(aw, data)
aw_result = bt.run(aw_backtest)

aw_result.plot(figsize=(10, 6), title='All Weather', legend=False)
plt.show()

# %%
from matplotlib import cm

ax = aw_result.get_security_weights().plot.area(figsize=(10,6),
                                                ylim=[0,1],
                                                legend=False,
                                                colormap=cm.jet)
handles, labels = ax.get_legend_handles_labels()
plt.margins(0,0)

plt.legend(reversed(handles),
           reversed(labels),
           loc='lower right',
           bbox_to_anchor=(1.15, 0))
plt.show()
# %%
aw_result.stats.loc[['total_return', 'cagr', 'daily_vol', 'max_drawdown', 'calmar', 'daily_sharpe']]


# %%
# 3. 동적 자산배분
import bt
import matplotlib.pyplot as plt

data = price.dropna()

gdaa = bt.Strategy('GDAA', [
    bt.algos.SelectAll(),
    bt.algos.SelectMomentum(n=5, lookback=pd.DateOffset(years=1)),
    bt.algos.WeighERC(lookback=pd.DateOffset(years=1)),
    bt.algos.RunMonthly(),
    bt.algos.Rebalance()
])

gdaa_backtest = bt.Backtest(gdaa, data)
gdaa_result = bt.run(gdaa_backtest)

gdaa_result.plot(figsize=(10, 6),
                 title='Global Dynamic Asset Allocation',
                 legend=False)
plt.show()

# %%
gdaa_result.stats

# %%
from matplotlib import cm

wt = gdaa_result.get_security_weights().reindex(columns=price.columns)
ax = wt.plot.area(figsize=(10, 6), ylim=[0, 1], legend=False, colormap=cm.jet)
handles, labels = ax.get_legend_handles_labels()
plt.margins(0, 0)
plt.legend(reversed(handles),
           reversed(labels),
           loc='lower right',
           bbox_to_anchor=(1.15, 0))
plt.show()
# %%
gdaa_backtest.turnover.plot(figsize=(10,6), legend=False) # 턴오버 -> 매매비용, 세금, 기타비용 등 발생

# %%
gdaa_backtest_net = bt.Backtest(gdaa, 
                                data, 
                                name='GDAA_net',
                                commissions=lambda q, p: abs(q) * p * 0.002) # q: 주수 / p: 주가
gdaa_result = bt.run(gdaa_backtest, gdaa_backtest_net)
# %%
gdaa_result.prices.plot(figsize=(10, 6),
                        title='Global Dynamic Asset Allocation')
plt.show()


# 4. 추세추종 전략 : 마켓 타이밍, 파라미터 최적화, 롱 숏 전략
# %%
# 4.1 마켓 타이밍
import pandas_ta as ta

data = price[['SPY']].dropna()
sma = data.apply(lambda x: ta.sma(x, 200))

import bt

bt_sma = bt.Strategy('Timing', [
    bt.algos.SelectWhere(data > sma),
    bt.algos.WeighEqually(),
    bt.algos.Rebalance()
])

bt_sma_backtest = bt.Backtest(bt_sma, data)

# %%
def buy_and_hold(data, name):

    # 벤치마크 전략 생성
    bt_strategy = bt.Strategy(name, [
        bt.algos.SelectAll(),
        bt.algos.WeighEqually(),
        bt.algos.RunOnce(),
        bt.algos.Rebalance()
    ])

    return bt.Backtest(bt_strategy, data)

# %%
stock = buy_and_hold(data[['SPY']], name='stock') # 벤치마크 전략 백테스트

# %%
bt_sma_result = bt.run(bt_sma_backtest, stock)

# %%
import matplotlib.pyplot as plt

bt_sma_result.prices.iloc[201:, ].rebase().plot(figsize=(10, 6))
plt.show()

# %%
bt_sma_result.prices.iloc[201:,].rebase().to_drawdown_series().plot(
    figsize=(10, 6))
plt.show()

# %%
bt_sma_result.stats.loc[[
    'total_return', 'cagr', 'daily_vol', 'max_drawdown', 'calmar', 'daily_sharpe', 'daily_sortino'
]]


# 4.2 파라미터 최적화
# %%
import bt
import pandas_ta as ta

data = price[['SPY']].dropna()

def timing(price, n):

    sma = price.apply(lambda x: ta.sma(x, n))
    strategy = bt.Strategy(n, [
        bt.algos.SelectWhere(price > sma),
        bt.algos.WeighEqually(),
        bt.algos.Rebalance()
    ])

    backtest = bt.Backtest(strategy, price)

    return (backtest)

n_20 = timing(data, 20)
n_60 = timing(data, 60)
n_100 = timing(data, 100)
n_150 = timing(data, 150)
n_200 = timing(data, 200)
n_250 = timing(data, 250)

result = bt.run(n_20, n_60, n_100, n_150, n_200, n_250)

# %%
from matplotlib import cm

result.prices[250:].rebase().plot(figsize=(10, 6), colormap=cm.jet)
plt.show()

# %%
# 4.3 롱숏 전략
import pandas_ta as ta

data = price[['SPY']]
SMA_200 = data.apply(lambda x: ta.sma(x, 200))
SMA_60 = data.apply(lambda x: ta.sma(x, 60))
# %%
signal = SMA_200.copy()
signal[SMA_60 > SMA_200] = 1
signal[SMA_60 < SMA_200] = -1
signal[signal.isnull()] = 0
# %%
import matplotlib.pyplot as plt
# %%
bind = pd.concat([data, SMA_200, SMA_60, signal], axis=1)

# %%
bind.columns = ['SPY', 'SMA 200', 'SMA 60', 'signal']

# %%
bind.loc['2018':].plot(figsize=(10., 6), secondary_y=['signal'])
plt.show()

# %%
import bt

strategy = bt.Strategy(
    'SMA_crossover',
    [bt.algos.SelectAll(),
     bt.algos.WeighTarget(signal),
     bt.algos.Rebalance()])
backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)

result.plot(figsize=(10,6))
plt.show()
# %%
result.display_monthly_returns()

# %%
pd.concat([bind, result.prices], axis=1).loc['2020'].plot(figsize=(10, 6), secondary_y=['signal'], alpha=0.8)


# %%
# 4.4 평균회귀 전략
## 1. RSI
import pandas_ta as ta


data = price[['SPY']]
spy_rsi = data.apply(lambda x: ta.rsi(x,14))

signal = spy_rsi.copy()
signal[spy_rsi > 70] = -1
signal[spy_rsi < 30] = 1
signal[(spy_rsi <= 70) & (spy_rsi >= 30)] = 0
signal[signal.isnull()] = 0

# %%
from matplotlib import gridspec
import matplotlib.pyplot as plt

fig = plt.subplots(figsize=(10,6), sharex=True)
gs = gridspec.GridSpec(nrows=2, ncols=1, height_ratios=[2,1])

ax1 = plt.subplot(gs[0])
ax1 = data['SPY'].plot()
ax1.set_xlabel('')
ax1.axes.xaxis.set_ticks([])

ax2 = plt.subplot(gs[1])
ax2 = spy_rsi['SPY'].plot(color='black', ylim=[0, 100])
ax2 = plt.axhline(y=30, color='red', linestyle='-')
ax2 = plt.axhline(y=70, color='red', linestyle='-')

plt.subplots_adjust(wspace=0, hspace=0)
plt.show()

# %%
import bt

strategy = bt.Strategy('RSI_MeanReversion',
                       [bt.algos.WeighTarget(signal),
                        bt.algos.Rebalance()])
backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)

result.plot(figsize=(10, 6))
plt.show()

# %%
result.stats.loc[['total_return', 'cagr', 'daily_vol', 'max_drawdown', 'calmar', 'daily_sharpe']]

# %%
## 2. 볼린저 밴드
import pandas as pd
band = ta.bbands(data['SPY'], length=20, std=2)

bb = pd.concat([band[['BBL_20_2.0_2.0', 'BBM_20_2.0_2.0', 'BBU_20_2.0_2.0']], data['SPY']], axis=1)
bb.columns = ['Upper Band', 'Mid Band', 'Lower Band', 'SPY']

# %%
import numpy as np

signal = data.copy()
signal['SPY'] = np.nan

# %%
signal[bb['SPY'] > bb['Upper Band']] = -1
signal[bb['SPY'] < bb['Lower Band']] = 1
signal[signal.isnull()] = 0

# %%
strategy = bt.Strategy('BB',
                       [bt.algos.WeighTarget(signal),
                        bt.algos.Rebalance()])
backtest = bt.Backtest(strategy, data)
result = bt.run(backtest)

result.plot(figsize=(10,6))
plt.show()

# %%
result.stats.loc[['total_return', 'cagr', 'daily_vol', 'max_drawdown', 'calmar', 'daily_sharpe']]

# %%
