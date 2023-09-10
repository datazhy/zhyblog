---
layout:       post
title:      "pip安装第三方库网速慢的解决方案"
subtitle:   "Solutions for Slow Internet Speed when Installing Third-Party Libraries with pip"
date:       2022-07-30 12:00:00
author:       "Zhy"
catalog:      true
header-style: text
tags:
    - Python
    - pip
---




## **前言**

Python之所以好用，并受到大家的喜爱，我想很多优质的第三方库是其中一个原因。例如爬虫我们使用的requests库，数据分析中的pandas库，机器学习中的sklearn库等。

* pandas
* numpy
* matplotlib 
* scipy
* sklearn
* ......

pip升级方式：

```coq  
pip install pip -U
```


安装第三方库（其他库同理）：

```coq
pip install pandas
```

更新方式为：

```coq
pip install --upgrade pandas
```


但是你会发现，国外的源下载速度实在太慢，容易下载超时。要想加速安装第三方库，其实我们只需要使用国内的镜像即可。


## **国内镜像加速**

```coq
清华：https://pypi.tuna.tsinghua.edu.cn/simple

阿里云：http://mirrors.aliyun.com/pypi/simple/

中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/

华中理工大学：http://pypi.hustunique.com/

山东理工大学：http://pypi.sdutlinux.org/ 

豆瓣：http://pypi.douban.com/simple/
```


### **临时使用**

```
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

### **设为默认**

升级 pip 到最新的版本 (>=10.0.0) 后进行配置：

```
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

设置成功后你的C:\Users\pip路径下会出现一个`pip.ini`配置文件如下图：

![](/img/in-post/pip-install.png)

`pip.ini`内容如下
```coq
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
[install]
trusted-host=mirrors.aliyun.com
```

### **注意**

如果你的 pip 默认源的网络连接较差，可以临时使用清华的镜像站来升级pip版本：

```coq
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
```
