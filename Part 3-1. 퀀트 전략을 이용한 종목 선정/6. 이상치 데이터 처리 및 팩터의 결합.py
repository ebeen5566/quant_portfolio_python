# %%
# 이상치(outlier) 포함 여부 -> 보정 여부
## 1. PBR 데이터 내 이상치 체크
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')

value_list = pd.read_sql("""
select * from kor_value
where 기준일 = (select max(기준일) from kor_value);
""", con=engine)

engine.dispose()

value_pbr = value_list[value_list['지표'] == 'PBR']

print(value_pbr['값'].max(), '\n', value_pbr['값'].min())
# %%

import matplotlib.pyplot as plt

value_pbr['값'].plot.hist(bins=100, figsize=(10, 6))
plt.xlim(0, 40)
plt.show()

# %%
## 2. 트림: 이상치 데이터 삭제 - 상하위 1% 데이터 삭제
q_low = value_pbr['값'].quantile(0.01)
q_hi = value_pbr['값'].quantile(0.99)

value_trim = value_pbr.loc[(value_pbr['값'] > q_low) & (value_pbr['값'] < q_hi),
                           ['값']]

value_trim.plot.hist(figsize=(10,6), bins=100, legend=False)
plt.show()

# %%
## 3. 윈저라이징(winsorizing): 이상치 데이터 대체
value_winsor = value_pbr[['값']].copy()
value_winsor.loc[value_winsor['값'] < q_low, '값'] = q_low
value_winsor.loc[value_winsor['값'] > q_hi, '값'] = q_hi

fig, ax = plt.subplots(figsize=(10,6))
n, bins, patches = plt.hist(value_winsor, bins=100)
patches[0].set_fc('red')
patches[-1].set_fc('red')
plt.show()

# %%
## 3. 팩터의 결합 방법 - 단순한 순위 합산은 한계 있음
### 여러 팩터를 동일 비중으로 투자하고자 할 경우, 각 순위는 분포의 범위가 다름
### 따라서 순위와 비중의 가중평균을 통해 포트폴리오 구성하면 왜곡된 결과가 발생함
value_pivot = value_list.pivot(index='종목코드', columns='지표', values='값')
value_rank = value_pivot.rank(axis=0)

fig, axes = plt.subplots(5, 1, figsize=(10, 6), sharex=True)
for n, ax in enumerate(axes.flatten()):
    ax.hist(value_rank.iloc[:, n])
    ax.set_title(value_rank.columns[n], size=12)

fig.tight_layout()
# %%
value_pivot.isna().sum()
# %%
## 대안 -> z-score
from scipy.stats import zscore

value_rank_z = value_rank.apply(zscore, nan_policy='omit')

fig, axes = plt.subplots(5, 1, figsize=(10,6), sharex=True, sharey=True)
for n, ax in enumerate(axes.flatten()):
    ax.hist(value_rank_z.iloc[:, n])
    ax.set_title(value_rank.columns[n], size=12)

fig.tight_layout()
plt.show()
# %%
