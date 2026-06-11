import seaborn as sns
import matplotlib.pyplot as plt

df = sns.load_dataset('penguins')

plt.scatter(df['flipper_length_mm'], df['body_mass_g'])

plt.show()

# type이 series로 바뀌는 이유는 groupby 함수를 써서가 아니라, 컬럼을 1개만 써서 그런 거임
df_group = df.groupby('species')['body_mass_g'].mean().reset_index()
plt.bar(x=df_group['species'], height=df_group['body_mass_g'])
plt.show()

plt.rc('font', family='Malgun Gothic')
plt.hist(df['body_mass_g'], bins=30)
plt.hist(df.loc[df['species']=='Gentoo']['body_mass_g'], bins=10)
plt.xlabel('Body Mass')
plt.ylabel('Count')
plt.title('펭귄의 몸무게 분포')
plt.show()

import pandas as pd
df_unrate = pd.read_csv(
      'https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE',
      parse_dates=['observation_date']
  )
df_unrate.info()

df = df_unrate.rename(columns={'observation_date':'DATE' , 'UNRATE':'VALUE'})
df.head()

df['DATE'] = pd.to_datetime(df['DATE'])
df.info()

plt.plot(df['DATE'], df['VALUE'])
plt.show()

# stateless
fig, axes = plt.subplots(2, 1, figsize=(10,6))
df = sns.load_dataset('penguins')

# 첫번째 차트
axes[0].scatter(df['flipper_length_mm'],df['body_mass_g'])
axes[0].set_xlabel('날개 길이(mm)')
axes[0].set_ylabel('몸무게(g)')
axes[0].set_title('날개와 몸무게 간의 관계')

# 두번째 차트
axes[1].hist(df['body_mass_g'], bins=30)
axes[1].set_xlabel('Body Mass')
axes[1].set_ylabel('Count')
axes[1].set_title('펭귄의 몸무게 분포')

# 간격 조정
plt.tight_layout()

plt.show()

# stateful
plt.figure(figsize=(10,6))

# 첫번째 그림
plt.subplot(2,1,1)
plt.scatter(df['flipper_length_mm'],df['body_mass_g'])
plt.xlabel('날개 길이(mm)')
plt.ylabel('몸무게(g)')
plt.title('날개와 몸무게 간의 관계')

# 두번째 그림
plt.subplot(2,1,2)
plt.hist(df['body_mass_g'], bins=30)
plt.xlabel('Body Mass')
plt.ylabel('Count')
plt.title('펭귄의 몸무게 분포')

# 간격 조정
plt.tight_layout()

plt.show()

# seaborn

import seaborn as sns

df = sns.load_dataset('titanic')
df.head()

sns.scatterplot(data=df, x='age', y='fare', hue='class', style='class')
plt.show()

df_pivot = df.pivot_table(index='class',
                          columns='sex',
                          values='survived',
                          aggfunc='mean'
                          )
df_pivot

sns.heatmap(df_pivot, annot=True, cmap='coolwarm')
plt.show()

sns.displot(data=df, x='age', hue='class', kind='hist', alpha=0.3)
plt.show()

sns.displot(data=df, x='age', col='class', row='sex', kind='hist')
plt.show()








