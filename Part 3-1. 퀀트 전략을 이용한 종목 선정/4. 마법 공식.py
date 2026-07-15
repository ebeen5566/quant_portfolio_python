# %%
# 1. 퀄리티와 밸류 간의 관계 (매출총이익 - PBR)
## 밸류 전략 Good - 위험 높은 종목은 가격이 낮음. but 저평가되었기에 밸류 지표(pbr, per 등)에 따라 투자하면 수익률 좋음
## 퀄리티 전략 Good - 우량주들은 시장에서 프리미엄이 붙어 가격이 높음. 그럼에도 수익성이 좋기에 장기적으로 수익률 좋음

from sqlalchemy import create_engine
import pandas as pd
import numpy as np

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')

value_list = pd.read_sql("""
select * from kor_value
where 기준일 = (select max(기준일) from kor_value)
and 지표 = 'PBR';
""", con = engine)

fs_list = pd.read_sql("""
select * from kor_fs
where 계정 in ('매출총이익', '자산')
and 공시구분 = 'y';
""", con=engine)

engine.dispose()


## 밸류 지표
value_list.loc[value_list['값'] < 0, '값'] = np.nan
value_pivot = value_list.pivot(index='종목코드', columns='지표', values='값')

## 퀄리티 지표
fs_list = fs_list.sort_values(['종목코드', '계정', '기준일'])
fs_list = fs_list.groupby(['종목코드', '계정']).tail(1)
fs_list_pivot = fs_list.pivot(index='종목코드', columns='계정', values='값')
fs_list_pivot['GPA'] = fs_list_pivot['매출총이익'] / fs_list_pivot['자산']

## 데이터 합치기
bind_rank = value_pivot['PBR'].rank().to_frame().merge(
    fs_list_pivot['GPA'].rank(ascending=False), how='inner', on='종목코드')

## 상관관계
bind_rank.corr()

# %%
## PBR의 분위수별 GPA 평균값 구하기
import matplotlib.pyplot as plt

bind_data = value_list.merge(fs_list_pivot, how='left', on='종목코드')
bind_data = bind_data.dropna()
bind_data['PBR_quantile'] = pd.qcut(bind_data['값'], q=5, labels=range(1, 6))
bind_group = bind_data.groupby('PBR_quantile').mean('GPA')

fig, ax = plt.subplots(figsize=(10, 6))
plt.rc('font', family='Malgun Gothic')
plt.bar(x=np.arange(5), height=bind_group['GPA'])
plt.xlabel('PBR')
plt.ylabel('GPA')

plt.show()

# %%
## french library 통한 비교 (Value vs Quality vs Best vs Worst)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

url = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/25_Portfolios_BEME_OP_5x5_CSV.zip'
df_qv = pd.read_csv(url, skiprows=23, encoding='cp1252', index_col=0)
end_point = np.where(pd.isna(df_qv.iloc[:,2]))[0][0]
df_qv = df_qv.iloc[0:end_point].apply(pd.to_numeric)

df_qv.head()

# %%
df_qv_quality = df_qv.loc[:, ['LoBM HiOP', 'BM2 OP5', 'BM3 OP5']].mean(axis=1)
df_qv_value = df_qv.loc[:, ['HiBM LoOP', 'BM5 OP2', 'BM5 OP3']].mean(axis=1)
df_qv_worst = df_qv.loc[:, ['LoBM LoOP', 'BM1 OP2', 'BM2 OP1', 'BM2 OP2']].mean(axis=1)
df_qv_best = df_qv.loc[:, ['HiBM HiOP', 'BM5 OP4', 'BM4 OP5', 'BM4 OP4']].mean(axis=1)
df_qv_bind = pd.concat([df_qv_quality, df_qv_value, df_qv_worst, df_qv_best], axis=1)
df_qv_columns = ['Quality', 'Value', 'Worst', 'Best']
df_qv_bind_cum = np.log(1 + df_qv_bind / 100).cumsum()

plt.rc('font', family='Malgun Gothic')
df_qv_bind_cum.plot(figsize=(10, 6),
                    colormap=cm.jet,
                    legend='reverse',
                    title='퀄리티/밸류별 누적 수익률')

plt.show()

# %%
# 2. 마법 공식 포트폴리오
## 이익수익률(earnings yield) - 이자 및 법인세 차감전이익 / 기업 가치
## 투하자본 수익률(return on capital) - 이자 및 법인세 차감전이익 / 투하자본
## 마법 공식 - 위 지표의 순위의 합 기준 상위 30~50개 종목을 1년간 보유한 후 매도하는 전략

from sqlalchemy import create_engine
import pandas as pd
import numpy as np

engine = create_engine('mysql+pymysql://root:@127.0.0.1:3306/stock_db')

ticker_list = pd.read_sql("""
select * from kor_ticker
where 기준일 = (select max(기준일) from kor_ticker)
    and 종목구분 = '보통주';
""", con = engine)

fs_list = pd.read_sql("""
select * from kor_fs    
where 계정 in ('당기순이익', '매출액', '법인세비용', '이자비용', '현금및현금성자산',
'부채', '유동부채', '유동자산', '비유동자산', '감가상각비')
and 공시구분 = 'q';
""", con = engine)

engine.dispose()

fs_list = fs_list.sort_values(['종목코드', '계정', '기준일'])
fs_list['ttm'] = fs_list.groupby(['종목코드', '계정'], as_index=False)['값'].rolling(window=4, min_periods=4).sum()['값']
fs_list_clean = fs_list.copy()
fs_list_clean['ttm'] = np.where(
    fs_list_clean['계정'].isin(['부채', '유동부채', '유동자산', '비유동자산']),
    fs_list_clean['ttm'] / 4, fs_list_clean['ttm'])

fs_list_clean = fs_list_clean.groupby(['종목코드', '계정']).tail(1)
fs_list_pivot = fs_list_clean.pivot(index='종목코드', columns='계정', values='ttm')

data_bind = ticker_list[['종목코드', '종목명', '시가총액']].merge(fs_list_pivot, how='left', on='종목코드')
data_bind['시가총액'] = data_bind['시가총액'] / 100000000
data_bind.head()

# %%
## 이익수익률 = (당기순이익 + 법인세비용 + 이자비용) / (시가총액 + 총부채 - (현금 - max(0, 유동부채 - 유동자산 + 현금)))
### 분자(EBIT)
magic_ebit = data_bind['당기순이익'] + data_bind['법인세비용'] + data_bind['이자비용']

### 분모(EV)
magic_cap = data_bind['시가총액']
magic_debt = data_bind['부채']

### 분모: 여유자금
magic_excess_cash = data_bind['유동부채'] - data_bind['유동자산'] + data_bind['현금및현금성자산']
magic_excess_cash[magic_excess_cash < 0] = 0
magic_excess_cash_final = data_bind['현금및현금성자산'] - magic_excess_cash

magic_ev = magic_cap + magic_debt - magic_excess_cash_final

### 이익수익률
magic_ey = magic_ebit / magic_ev

# %%
## 투하자본 수익률 = (당기순이익 + 법인세 + 이자비용) / {(유동자산 - 유동부채) + (비유동자산 - 감가상각비)}

magic_ic = (data_bind['유동자산'] - data_bind['유동부채']) + (data_bind['비유동자산'] - data_bind['감가상각비'])
magic_roc = magic_ebit / magic_ic

# %%
data_bind['이익수익률'] = magic_ey
data_bind['투하자본 수익률'] = magic_roc

magic_rank = (magic_ey.rank(ascending=False, axis=0) + 
              magic_roc.rank(ascending=False, axis=0)).rank(axis=0)
data_bind.loc[magic_rank <= 20, ['종목코드', '종목명', '이익수익률', '투하자본 수익률']].round(4)

# %%
import matplotlib.pyplot as plt
import seaborn as sns

data_bind['투자구분'] = np.where(magic_rank <= 20, '마법 공식', '기타')
plt.subplots(1, 1, figsize =(10, 6))
plt.rc('font', family='Malgun Gothic')
sns.scatterplot(data=data_bind,
                x='이익수익률',
                y='투하자본 수익률',
                hue='투자구분',
                style='투자구분',
                s=200)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.show()

# %%
