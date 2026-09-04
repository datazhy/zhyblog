---
layout:       post
title:      "英国某电商如何精细划分在线零售客户群体"
subtitle:   "How a UK E-commerce Firm Precisely Segments Its Online Retail Customers"
description:  "基于 Kaggle 英国在线零售数据集，用 Python 做数据清洗与探索性分析，再结合 RFM 模型与 K-Means 聚类，把客户细分为高价值、重点深耕、挽留、流失等群体。"
date:       2022-07-31 12:00:00 +0800
author:       "Zhy"
catalog:      true
header-style: text
lang:         zh-CN
translation_url: /en/2022/07/31/UK-Online-Retail-Customers/
tags:
    - Python
    - 客户分群
    - RFM
    - K-Means
    - 聚类分析
---




## **前言**

这是一个来自 Kaggle 的跨国数据集，包含英国某电商在线零售在 **2010 年 12 月 1 日到 2011 年 12 月 9 日**之间发生的交易数据。数据量庞大，很适合用机器学习中的 K-Means 等算法，根据客户在市场上的购买行为来做精细化分群。

本文的思路是：先做数据清洗与探索性分析摸清整体情况，再用 **RFM 模型**做人工分层，最后用 **K-Means 聚类**做无监督分群，两种方法相互印证。

## **数据来源**
<https://www.kaggle.com/yasserh/customer-segmentation-dataset>   
<https://archive.ics.uci.edu/ml/datasets/online+retail>

## **数据说明**
该数据集共 540545 行，8 列，具体字段信息为：  

| 字段 | 说明 |
| ------ | ----------- |
| InvoiceNo | 发票号码，一个唯一分配给每笔交易的 6 位整数。若以字母「c」开头，表示取消 |
| StockCode | 商品编码 |
| Description | 产品（项目）名称 |
| Quantity | 数量 |
| InvoiceDate | 发票日期 |
| UnitPrice | 单价，以英镑为单位的每单位产品价格 |
| CustomerID | 客户 ID |
| Country | 国家 |

## **问题描述**

- 数据的预处理、数据清洗，对数据集做探索性分析 

- 基于客户的相似性进行细分，建立 RFM 人群画像与 K-Means 聚类模型  

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
![预处理后的在线零售交易数据前 20 行预览](/img/in-post/uk-retail-01-data-preview.png)


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
![全球订单分布地图，零售订单以英国为中心辐射欧洲，北美、南美、澳大利亚亦有涉及](/img/in-post/uk-retail-02-transaction-status.png)
![探索性分析四联图：订单交易成功率、地区消费 Top7、订单逐月变化趋势、热门商品 Top7](/img/in-post/uk-retail-03-eda.png)


###  **结论**

- `英国为订单数量最多的国家` 

在全球订单分布区域中，零售订单主要分布在以英国为中心辐射的欧洲地区，此外北美、南美以及澳大利亚均有国家地区涉及下单。

- `存在少量取消订单或退货`    

在所有订单中，成功交易的订单占比达到 **97.81%**，有 **2.19%** 的订单为取消订单或退货。

- `2011 年 11 月是订单高峰月`

2011 年 8 月到 2011 年 11 月订单数量上升明显。

- `热门商品`

最受欢迎的商品 Top 1：`WHITE HANGING HEART T-LIGHT HOLDER`。


## **基于 RFM 模型的客户分群**

RFM 从三个维度刻画客户价值：**R（Recency，最近一次消费距今天数）、F（Frequency，消费频率）、M（Monetary，消费总金额）**。下面先把三个指标分箱打分，再按均值划分「高/低」，从而拼出客户类型。

```python
## 计算每位顾客的消费总金额
df_total=pd.DataFrame(df.groupby('CustomerID')['Amount'].sum()).reset_index()
df_total.columns = ['CustomerID','Total_Amount']
df_total['Total_Amount'] = df_total['Total_Amount'].map(lambda x:round(x,2))

## 提取各订单消费年月日与时间
df['InvoiceDate_ymd'] = df['InvoiceDate'].map(lambda x:x.split(' ')[0])
df['InvoiceDate_hms'] = df['InvoiceDate'].map(lambda x:x.split(' ')[1])

## RFM 级别划分 Step1
## 若数值越小，表示级别越高
df_rfm['R_level'] = pd.cut(df_rfm['R'],bins=[0,65,130,195,260,325,390],labels=[1,2,3,4,5,6],right=False)
df_rfm['F_level'] = pd.cut(df_rfm['F'],bins=[0,10,20,50,100,175,250],labels=[6,5,4,3,2,1],right=False)
df_rfm['M_level'] = pd.cut(df_rfm['M'],bins=[0,28,280,2800,28000,145000,285000],labels=[6,5,4,3,2,1],right=False)

## RFM 级别划分 Step2
df_rfm['R_level'] = df_rfm['R_level'].map(lambda x:'高' if x < df_rfm['R_level'].astype(int).mean() else '低')
df_rfm['F_level'] = df_rfm['F_level'].map(lambda x:'高' if x < df_rfm['F_level'].astype(int).mean() else '低')
df_rfm['M_level'] = df_rfm['M_level'].map(lambda x:'高' if x < df_rfm['M_level'].astype(int).mean() else '低')

## 代码较长，为节省篇幅部分已隐藏
```
![RFM 客户价值类型分布饼图：重点深耕客户占比 53.6% 最大，其次是重点挽留客户 15.33%](/img/in-post/uk-retail-04-rfm-a.png)
![各客户价值类型在 R/F/M 三个维度上的箱线图分布对比](/img/in-post/uk-retail-05-rfm-b.png)

###  **结论**

通过 RFM 模型人工对客户类型进行划分，`占比最大的是重点深耕客户（53.6%），其次是重点挽留客户（15.33%），占比最少的是重点唤回客户（0.09%）`。

##  **基于 K-Means 的聚类分析**

RFM 是靠人工设定阈值来分层，接下来用 K-Means 做一次无监督聚类，看数据本身会自然分成几群。

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
![肘部法则曲线：K=4 之后平均畸变程度趋于平缓](/img/in-post/uk-retail-06-elbow.png)
  

###  **k 定义**
当 K=4 时，平均畸变程度变化趋于平缓，此时改变 K 值对聚类效果影响不大，故确定聚类簇数为 4。 

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
![四类聚类客户在 R/F/M 三个维度上的显著特征雷达对比图](/img/in-post/uk-retail-07-clusters.png)

### **结论**

#### `第一类客户`  
该类客户上一次购物距今间隔较长，购物频率为 0，且购物总金额较少，为典型的**流失客户**。
  
#### `第二类客户` 
该类客户上一次购物距今间隔为 0，购物频率很高，且花费总金额很大，为典型的**高价值客户**。

#### `第三类客户` 
该类客户与第 1 类客户有很多相似的地方，不同之处在于该类客户仍有购物次数，但不高，为典型的**重要挽回客户**。
  
#### `第四类客户`  
该类客户上一次购物距今间隔较短，购物频率较低，且花费总金额为 0，可能为**新客户**。

## **总结**

从探索性分析到 RFM 分层，再到 K-Means 聚类，两条路径给出的结论是一致的：这家电商的客户里，**高价值 / 重点深耕客户贡献了绝大部分消费额，但数量上占比有限，大量客户处于流失或低频状态**。对运营而言，这意味着资源应重点投向维系高价值客户、唤回流失客户，并针对新客户设计转化路径——这正是精细化分群的意义所在。
