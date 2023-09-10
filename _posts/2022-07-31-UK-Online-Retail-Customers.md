---
layout:       post
title:      "英国某电商如何精细划分在线零售客户群体"
subtitle:   "How a UK E-commerce Firm Precisely Segments Its Online Retail Customers"
date:       2022-07-31 12:00:00
author:       "Zhy"
catalog:      true
header-style: text
tags:
    - Python
    - 客户分群
    - RFM
    - K-Means
    - 聚类分析
---



## **前言**

这是一个来自Kaggle的跨国数据集，其中包含在 2010 年 1 月 12 日到 2011 年 9 月 12 日之间发生的英国某电商在线零售的交易数据。
数据量很庞大，在分析思路上可以使用机器学习K-Means 等算法，根据客户在市场上的购买行为来细分客户。

## **数据来源**
<https://www.kaggle.com/yasserh/customer-segmentation-dataset>   
<https://archive.ics.uci.edu/ml/datasets/online+retail>

## **数据说明**
该数据集共540545行，8列，具体字段信息为：  

| Syntax | Description |
| ------ | ----------- |
| InvoiceNo | 发票号码，一个唯一分配给每笔交易的 6 位整数。如果此代码以字母“c”开头，则表示取消 |
| StockCode | 股票代码 |
| Description | 描述，产品（项目）名称 |
| Quantity | 数量 |
| InvoiceDate | 发票日期 |
| UnitPrice | 单价，以英镑为单位的每单位产品价格 |
| CustomerID | 客户ID |
| Country | 国家 |

## **问题描述**

- 数据的预处理，数据清洗，对数据集探索性分析 

- 对基于客户的相似性进行细分，建立RFM人群画像，K-Means 聚类模型  

- 调参并比较各种分类算法的评估指标  

## **导入第三方库**
```python
import pandas as pd 
import numpy as np 
from pyecharts.charts import *
import pyecharts.options as opts 

import warnings
warnings.filterwarnings('ignore')
```

## **数据预处理**
```python
## 数据读取
df = pd.read_excel('D:/**/Online Retail.xlsx')

## 缺失值处理
df.dropna(subset=['CustomerID'],inplace=True)

## 时间处理
df['InvoiceDate'] = df['InvoiceDate'].map(lambda x: str(x))

## 国家名称统一化
df.replace({'EIRE':'Ireland','USA':'United States','RSA':'South Africa','Czech Republic':'Czech','Channel Islands':'United Kingdom'},
        inplace=True)
        
## 计算每单的价格
df['Amount'] = df['Quantity']*df['UnitPrice']
```

## 预处理后的数据预览

```python
df.head(20)
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/5c36f30dc92a4cfc9497b029b6c8153c.png#pic_center)


##  **数据探索性分析**

```python
## 订单交易状态
df['InvoiceNo'] = df['InvoiceNo'].astype(str)
df['Transaction status'] = df['InvoiceNo'].map(lambda x:'0' if x.startswith('C') else '1')

## 可视化——订单交易状态
label = ['交易成功','交易取消']
value = df['Transaction status'].value_counts().values.tolist()

## 代码较长，为节省篇幅部分已隐藏
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/7008cf6127af4c7e809fcaed2546ae5d.png#pic_center)
![在这里插入图片描述](https://img-blog.csdnimg.cn/f9aec5912fdb411295110e8e735d3fd4.png#pic_center)


###  **结论**

- `英国为订单数量最多的国家` 

在全球订单分布区域中，零售订单主要分布在以英国为中心辐射的欧洲地区，此外，北美、南美以及澳大利亚均有国家地区涉及订单下单

- `存在少量取消订单或退货`    

在所有订单中，成功交易的订单占比达到97.81%，有2.19%的订单为取消订单或退货

- `2011年11月是订单高峰月`

2011年8月到2011年11月订单数量上升明显

- `热门商品`

最受欢迎的商品Top 1: `WHITE HANGING HEART T-LIGHT HOLDER`


## **基于RFM模型的客户分群**

```python
## 计算每位顾客的消费总金额
df_total=pd.DataFrame(df.groupby('CustomerID')['Amount'].sum()).reset_index()
df_total.columns = ['CustomerID','Total_Amount']
df_total['Total_Amount'] = df_total['Total_Amount'].map(lambda x:round(x,2))

## 提取各订单消费年月日与时间
df['InvoiceDate_ymd'] = df['InvoiceDate'].map(lambda x:x.split(' ')[0])
df['InvoiceDate_hms'] = df['InvoiceDate'].map(lambda x:x.split(' ')[1])

## RFM级别划分Step1
## 若数值越小，表示级别越高
df_rfm['R_level'] = pd.cut(df_rfm['R'],bins=[0,65,130,195,260,325,390],labels=[1,2,3,4,5,6],right=False)
df_rfm['F_level'] = pd.cut(df_rfm['F'],bins=[0,10,20,50,100,175,250],labels=[6,5,4,3,2,1],right=False)
df_rfm['M_level'] = pd.cut(df_rfm['M'],bins=[0,28,280,2800,28000,145000,285000],labels=[6,5,4,3,2,1],right=False)

## RFM级别划分Step2
df_rfm['R_level'] = df_rfm['R_level'].map(lambda x:'高' if x < df_rfm['R_level'].astype(int).mean() else '低')
df_rfm['F_level'] = df_rfm['F_level'].map(lambda x:'高' if x < df_rfm['F_level'].astype(int).mean() else '低')
df_rfm['M_level'] = df_rfm['M_level'].map(lambda x:'高' if x < df_rfm['M_level'].astype(int).mean() else '低')

## 代码较长，为节省篇幅部分已隐藏
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/50b08d83c8f247c6be55444c9957a5a0.png#pic_center)
![在这里插入图片描述](https://img-blog.csdnimg.cn/156ac8baed3d498f90694a2326f909d8.png#pic_center)

###  **结论**

通过RFM模型人工的对客户类型进行划分，`占比最大的是重点深耕客户，其次是重点挽留客户，占比最少的是重点唤回客户`

##  **基于K-Means的聚类分析**

```python
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

K = range(1, 10)
meandistortions = []
for k in K:
    kmeans = KMeans(n_clusters=k)
    kmeans.fit(data_scaled)
    meandistortions.append(sum(np.min(cdist(data_scaled, kmeans.cluster_centers_, 'euclidean'), axis=1))/data_scaled.shape[0])
plt.plot(K, meandistortions, marker='o')
plt.xlabel('K')
plt.ylabel('Average distortion degree')
plt.title('Use the Elbow Method to select the best K value')
plt.show()

# 代码较长，为节省篇幅部分已隐藏
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/675be53ebd5f43ad87c33ffd3582cb1e.png#pic_center)
  

###  **k定义**
当K=4时，平均畸变程度变化趋于平缓，此时改变K值对聚类效果影响不大，故确定聚类簇数为4。 

###  **聚类结果可视化**

```python
Kmeans = KMeans(n_clusters=4,max_iter=50)
Kmeans.fit(data_scaled)
cluster_labels_k = Kmeans.labels_
df_rfm = df_rfm.reset_index()
cluster_labels = pd.DataFrame(cluster_labels_k, columns=['clusters'])
res = pd.concat((df_rfm, cluster_labels), axis=1)

## 代码较长，为节省篇幅部分已隐藏
```
![在这里插入图片描述](https://img-blog.csdnimg.cn/4b4017606d514073b0e1b6073eeddee2.png#pic_center)

### **结论**

#### `第一类客户`  
该类客户上一次购物距今间隔较长，购物频率为0，且购物总金额较少，为典型的流失客户
  
#### `第二类客户` 
该类客户上一次购物距今间隔为0，购物频率很高，且花费总金额很大，为典型的高价值客户

#### `第三类客户` 
该类客户与第1类客户有很多相似的地方，不同之处在于该类客户仍有购物次数，但不高，为典型的重要挽回客户
  
#### `第四类客户`  
该类客户上一次购物距今间隔较短，购物频率较低，且花费总金额为0，可能为新客户