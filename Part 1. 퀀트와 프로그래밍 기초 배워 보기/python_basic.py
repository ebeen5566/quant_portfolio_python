# 2.1 상수와 변수
var = 10
print(var)

var= "Hello, World!"
print(var)

var1 = 1
var2 = 2
print(var1 + var2)

var1 = 3
print(var1 + var2)

type(1)
type(1.0)

name = "이용빈"
birth = '1997'

f'안녕하세요, {name}님! 당신은 {birth}년에 태어났군요!'

var = "퀀트 투자 포트폴리오 만들기"
var.replace(" ", "_")

a = 'Life is short, You need Python'
len(a)

list1 = var.split(' ')
print(list1)
list1 = []
print(list1)

var = 'quant'
print(var[2])
print(var[-1])

var[2]

a = []
type(a)

var = [1,2,['a','b']]
var[0]
var[2][0]

var[0:2]

var = [1,2,3]
var.append([4,5])
print(var)

var = [1,2,3]
var.extend([4,5])
print(var)

var = [1,2,3]
del var[0]
print(var)

var = [1,2,3]
var[0:2] = []
print(var)

var = [2,4,1,3]
var.sort()
print(var)

import datetime

var = datetime.datetime.now()   
var
type(var)

var.time()

var = datetime.datetime.now()   
var.strftime('%Y-%m-%d %H:%M:%S')

import pandas as pd

dict_data = {'a':1, 'b':2, 'c':3}
series = pd.Series(dict_data)
print(series)

type(series)

series.values

list_data = ['a','b','c']
series_2 = pd.Series(list_data)
print(series_2)

series_3 = pd.Series(list_data, index=['index1','index2','index3'])
print(series_3)

capital = pd.Series({'Korea':'Seoul', 
                     'Japan':'Tokyo', 
                     'China':'Beijing',
                     'USA':'Washington D.C.',
                     'UK':'London',
                     'France':'Paris'})

print(capital)

capital['Korea']

capital[['Korea', 'Japan']]

capital.iloc[[0,3]]

capital.iloc[0]
capital[0:3]

series_1 = pd.Series([1,2,3])
series_2 = pd.Series([4,5,6])

series_1 + series_2
series_1 * 2

dict_data = {'col1':[1,2,3], 'col2':[4,5,6], 'col3':[7,8,9]}
df = pd.DataFrame(dict_data, index=['a','b','c'])
print(df)

type(df)

df2 = pd.DataFrame([[1,2,3],[4,5,6],[7,8,9]], columns=['col1', 'col2', 'col3'], index=['a','b','c'])
df2

df2.index = ['index1', 'index2', 'index3']
df2.columns = ['column1', 'column2', 'column3']
df2

df2.rename(index={'index1':'첫번째 행'}, inplace=True)
df2.rename(columns={'column1':'첫번째 열'}, inplace=True)

df2

df2.drop('index3', axis=0, inplace=True)
df2.drop('column3', axis=1, inplace=True)
df2

new_row = pd.DataFrame([[7,8]], columns=['column1', 'column2'], index=['index3'])
df2 = pd.concat([df2, new_row])
df2

df2['column3'] = [3,6,9]
df2

import pandas as pd
dict_data = {'col1':[1,2,3,4], 'col2':[5,6,7,8], 'col3':[9,10,11,12]}
df = pd.DataFrame(dict_data, index=['index1','index2','index3','index4'])
df

# 열 불러올 때 - 걍 대괄호 2개라고 생각하샘
df['col1']
df.col1
type(df['col1'])

df[['col1']]
df[['col1','col2']]
type(df[['col1','col2']])

df[['col1','col3']]

# 행 불러올 때 - loc, iloc 함수 쓴다
df.loc['index1']
type(df.loc['index1'])
df.iloc[0]

df.loc[['index1']]
df.iloc[[0]]
# 왠만해서 Series로 반환되는 경우는 없다고 생각하는게 좋음
# 그냥 대괄호 2개 쓰자

df.loc['index1' : 'index2']
type(df.loc['index1' : 'index2'])
# 2개 이상 인덱싱하면 그냥 데이터프레임이다

df.loc['index1','col1']
df.loc[['index1','index3'],['col1','col3']]

df.loc['index1':'index2','col1':'col3']

#인덱싱
df.iloc[0,0]
df
df.iloc[[0,2],[0,2]]

#슬라이싱
df.iloc[0:2,0:3]

data_csv = pd.read_csv('kospi_2025.csv')
data_csv

data_csv = pd.read_csv('https://raw.githubusercontent.com/ebeen5566/system_trading/main/kospi_2025.csv')
df = data_csv
df.columns = ['Date' , 'Close' , 'Ret(%)']
df.index = df.index+1
df = df.fillna(0)
df.to_csv('kospi_2025_revised.csv', index=False)

df.head(5)
df.tail(5)

import seaborn as sns

df = sns.load_dataset('titanic')
df.head()
df.tail()
df.shape   

df['sex'].value_counts()

df[['sex', 'survived']].value_counts()
df[['sex', 'survived']].value_counts(normalize=True).sort_index()

df['survived'].mean()
# 컬럼
df[['survived' , 'age']].mean()

df['fare'].min()
df[['fare']].min()
df['fare'].max()
df['fare'].mean()
df['fare'].median()
len(df['fare'])

df.head()
df.info()
df.head().isnull()

len(df.dropna())

df.dropna(subset='age' , axis=0)
df.dropna(axis=1)

df.dropna(axis=1, thresh=300)

df_2 = df.copy()
df_2.head(6)

mean_age = df_2['age'].mean()
print(mean_age)

df_2['age'] = df_2['age'].fillna(mean_age)
df_2.head(6)

df_2['age'].head(10)

df_2['embark_town'].value_counts()
df_2['embark_town'] = df_2['embark_town'].fillna('Southampton')

df_2[['deck']].head(10)
df_2['deck_ffill'] = df_2['deck'].ffill()
df_2['deck_bfill'] = df_2['deck'].bfill()

df_2[['deck', 'deck_ffill', 'deck_bfill']].head(10)

df = sns.load_dataset('mpg')
df.head()

df.info()
df.set_index('name', inplace=True)
df.head()

df.sort_index(inplace=True)
df.head()

df.sort_index(inplace=True, ascending=False)
df.head()

df.reset_index(inplace=True)    
df.head()

df = sns.load_dataset('mpg')
df.tail()

df['cylinders'].unique()

filter_bool = (df['cylinders'] == 4)
filter_bool.tail(10)

type(filter_bool)

df.loc[filter_bool,]

filter_bool_2 = (df['cylinders'] == 4) & (df['horsepower'] >= 100)
df.loc[filter_bool_2, ['cylinders', 'horsepower' , 'name']]

filter_isin = df['name'].isin(
    ['ford maverick' , 'ford mustang ii' , 'chevrolet impala']
)

df.loc[filter_isin,].sort_values(by='name', ascending=False)

df['ratio'] = (df['mpg'] / df['weight']) * 100
df.head(10)

df[['mpg' , 'weight' , 'ratio']]

import numpy as np

num = pd.Series([-2, -1, 1, 2])
# 인덱스 반환
np.where(num >= 0)

num.loc[np.where(num >= 0)]

np.where(num >= 0, '양수', '음수')

df['horse_power_div'] = np.where(
    df['horsepower'] < 100 , '100 미만',
    np.where((df['horsepower'] >= 100) & (df['horsepower'] < 200) , '100 이상',
    np.where((df['horsepower'] >= 200) , '200 이상' , '기타')
    )
)
df.head(10)
df['horse_power_div'].value_counts()

df1 = pd.DataFrame({
    "A": ["A0" , "A1" , "A2" , "A3"],
    "B": ["B0" , "B1" , "B2" , "B3"],
    "C": ["C0" , "C1" , "C2" , "C3"],
    "D": ["D0" , "D1" , "D2" , "D3"]
},
    index=[0,1,2,3],
)

df2 = pd.DataFrame({
    "A": ["A4" , "A5" , "A6" , "A7"],
    "B": ["B4" , "B5" , "B6" , "B7"],
    "C": ["C4" , "C5" , "C6" , "C7"],
    "D": ["D4" , "D5" , "D6" , "D7"]
},
    index=[4,5,6,7],
)

df3 = pd.DataFrame({
    "A": ["A8" , "A9" , "A10" , "A11"],
    "B": ["B8" , "B9" , "B10" , "B11"],
    "C": ["C8" , "C9" , "C10" , "C11"],
    "D": ["D8" , "D9" , "D10" , "D11"]
},
    index=[8,9,10,11],
)

result = pd.concat([df1,df2,df3])
result

df4 = pd.DataFrame({
    "B":["B2","B3","B4","B5"],
    "D":["D2","D3","D6","D8"],
    "F":["F2","F3","F6","F7"]
},
    index=[2,3,6,7],
)

df4
result = pd.concat([df1, df4])
result

result = pd.concat([df1, df4],ignore_index=True)
result

result = pd.concat([df1,df4], axis=1)
result

result = pd.concat([df1,df4], axis=1, join='inner')
result

s1 = pd.Series(["X0" , "X1" , "X2" , "X3"], name ="X")
result = pd.concat([df1,s1], axis=1)
result

left = pd.DataFrame({
    "key":["K0","K1","K2","K3"],
    "A":["A0", "A1", "A2", "A3"],
    "B":["B0","B1","B2","B3"]
})

right = pd.DataFrame({
    "key":["K0","K1","K3","K4"],
    "C":["C0", "C1", "C3", "C4"],
    "D":["D0","D1","D3","D4"]
})
#자동으로 inner join 됨
result = pd.merge(left, right, on='key')
result

result = pd.merge(left, right, on='key', how='left')
result

result = pd.merge(left, right, on='key', how='right')
result

result = pd.merge(left, right, on='key', how='outer')
result

left = pd.DataFrame({
    "key_left":["K0","K1","K2","K3"],
    "A":["A0", "A1", "A2", "A3"],
    "B":["B0","B1","B2","B3"]
})

right = pd.DataFrame({
    "key_right":["K0","K1","K3","K4"],
    "C":["C0", "C1", "C3", "C4"],
    "D":["D0","D1","D3","D4"]
})

result = pd.merge(left, right, left_on='key_left'
                  , right_on='key_right', how='inner')

result

left = pd.DataFrame({
    "A":["A0", "A1", "A2", "A3"],
    "B":["B0","B1","B2","B3"]},
    index=["K0","K1","K2","K3"]
    )

right = pd.DataFrame({
    "C":["C0", "C1", "C3", "C4"],
    "D":["D0","D1","D3","D4"]},
    index=["K0","K1","K3","K4"]
    )

result = left.join(right)
result

df = sns.load_dataset('penguins')
df.head()
df.info()
df
df_melt = df.melt(id_vars=['species','island'])
df_melt.info()
df_melt.head()

import pandas as pd
import seaborn as sns

df_pivot_1 = df.pivot_table(
    index='species',columns='island',
    values='bill_length_mm',aggfunc='mean'
)
df_pivot_1

df_pivot_2=df.pivot_table(
    index=['species','sex'],columns='island',
    values=['bill_length_mm','flipper_length_mm'],
    aggfunc=['mean','count']
)

df_pivot_2

df_pivot_4 = df.pivot_table(
    index=['species','sex'],columns='island',
    values='bill_length_mm',aggfunc='mean'
)

df_pivot_4

df_pivot_4.stack()

df_pivot_4.stack().to_frame()

df_pivot_4.unstack()

bill_length_mm = df['bill_length_mm']
bill_length_mm.head()

import numpy as np

result = bill_length_mm.apply(np.sqrt)
result.head()

def mm_to_cm(num):
    return num/10

result_2 = bill_length_mm.apply(mm_to_cm)
result_2.head()

df_num = df[['bill_length_mm','bill_depth_mm','flipper_length_mm','body_mass_g']]
df_num
df_num.apply(max,axis=0)

def num_null(data):
    null_vec = pd.isnull(data)
    null_count = np.sum(null_vec)

    return null_count

df_num.apply(num_null)

df.head()

df_group = df.groupby(['species'])
df_group
df_group.head(2)

for key,group in df_group:
    print(key)
    print(group.head(2))

df_group[['bill_length_mm','bill_depth_mm','flipper_length_mm','body_mass_g']].mean()

df.groupby(['species','sex'])[['bill_length_mm','bill_depth_mm','flipper_length_mm','body_mass_g']].mean()

def min_max(x):
    return x.max() - x.min()

df.groupby(['species'])['bill_length_mm'].agg(min_max)

df.groupby(['species'])[['bill_length_mm','bill_depth_mm','flipper_length_mm','body_mass_g']].agg(['max','min'])

df.groupby(['species']).agg({'bill_length_mm':['max','min'] , 'island':['count']})

df.groupby(['species'])['bill_length_mm'].transform('mean')

def z_score(x):
    z = (x - x.mean()) / x.std()
    return z

df.groupby(['species'])['bill_length_mm'].transform(z_score)
df.groupby(['species'])['bill_length_mm'].apply(min)
df.groupby(['species'])['bill_length_mm'].apply(z_score)

df.groupby(['species'])['bill_length_mm'].mean()

df.groupby(['species']).filter(lambda x: x['bill_length_mm'].mean() >= 40)

# 3.13 시계열 데이터 다루기

df = sns.load_dataset('taxis')
df.head()
df.info()

df['pickup'] = pd.to_datetime(df['pickup'])
df['dropoff'] = pd.to_datetime(df['dropoff'])

df['pickup'][0].year
df['pickup'][0].month

df['year'] = df['pickup'].dt.year
df['month'] = df['pickup'].dt.month
df['day'] = df['pickup'].dt.day
df[['pickup','year','month','day']].head()

df.sort_values('pickup', inplace=True)
df.head(5)
df.tail(5)
df.reset_index(drop=True, inplace=True)
df

df['dropoff'] - df['pickup']
df.set_index('pickup', inplace=True)
df.head()

df.index

df.loc['2019-02']
df.loc['2019-03-01':'2019-03-31']

pd.date_range(start='2025-01-01', end='2025-12-31', freq='ME')
pd.date_range(start='2025-01-01', end='2025-12-31', freq='3D')
pd.date_range(start='2025-01-01', end='2025-12-31', freq='W-MON')
pd.date_range(start='2025-01-01', end='2025-12-31', freq='WOM-2THU')
pd.date_range(start='2025-01-01', end='2025-12-31', freq='WOM-2FRI')






