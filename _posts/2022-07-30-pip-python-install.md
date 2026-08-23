---
layout:       post
title:      "pip 安装第三方库网速慢的解决方案"
subtitle:   "Solutions for Slow Internet Speed when Installing Third-Party Libraries with pip"
description:  "pip 从国外源下载第三方库太慢、容易超时？换用清华、阿里云、腾讯云等国内镜像即可提速。本文给出临时使用与永久配置两种方法，并附各平台 pip 配置文件路径。"
date:       2022-07-30 12:00:00 +0800
author:       "Zhy"
catalog:      true
header-style: text
tags:
    - Python
    - pip
---




## **前言**

Python 之所以好用、受到大家喜爱，很多优质的第三方库是其中一个重要原因。例如爬虫常用的 requests 库、数据分析中的 pandas 库、机器学习中的 sklearn 库等。

* pandas
* numpy
* matplotlib 
* scipy
* sklearn
* ......

pip 自身升级方式：

```bash
pip install pip -U
```


安装第三方库（其他库同理）：

```bash
pip install pandas
```


更新已安装的库：

```bash
pip install --upgrade pandas
```


但你会发现，从国外的默认源（PyPI 官方源）下载速度实在太慢，容易下载超时。要想加速安装第三方库，其实我们只需要把下载源换成国内的镜像即可。


## **国内镜像源**

以下均为当前可用、更新及时的主流镜像（推荐优先用清华或阿里云）：

```text
清华大学：   https://pypi.tuna.tsinghua.edu.cn/simple
阿里云：     https://mirrors.aliyun.com/pypi/simple/
腾讯云：     https://mirrors.cloud.tencent.com/pypi/simple/
华为云：     https://repo.huaweicloud.com/repository/pypi/simple/
中科大：     https://pypi.mirrors.ustc.edu.cn/simple/
```

> 提示：早年常被推荐的**豆瓣、华中理工、山东理工**等镜像大多已停止服务或长期不可用，不建议再用。另外镜像**同步会有延迟**，如果某个库刚发新版在镜像上还搜不到，临时切回官方源 `https://pypi.org/simple` 安装即可。


### **临时使用（只对本次命令生效）**

用 `-i` 参数临时指定源，适合偶尔换源：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```


### **设为默认（永久生效）**

先把 pip 升级到较新的版本（≥10.0.0）再配置：

```bash
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

执行成功后，pip 会自动写入配置文件。**不同系统的配置文件位置不同：**

| 系统 | 配置文件路径 |
| --- | --- |
| Windows | `%APPDATA%\pip\pip.ini`（旧版也可能在 `C:\Users\你的用户名\pip\pip.ini`） |
| macOS | `~/.config/pip/pip.conf`（或 `~/.pip/pip.conf`） |
| Linux | `~/.config/pip/pip.conf`（或 `~/.pip/pip.conf`） |

以 Windows 为例，配置文件如下图所示：

![Windows 用户目录下自动生成的 pip.ini 配置文件](/img/in-post/pip-install.png)

其内容大致如下：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

> 注意：`trusted-host` 要和 `index-url` 的**主机名保持一致**。它的作用是对**非 HTTPS（http 开头）**的源跳过 SSL 校验；上面清华源本身是 https，其实可以不写 `trusted-host`。只有当你用的是 http 源、或遇到 SSL 报错时才需要，且必须填对应的主机名（原来那种 index 指向清华、trusted-host 却写阿里云的写法是错的，不会生效）。


### **补充：临时用镜像升级 pip**

如果你的默认源网络较差，连 pip 自身都升级不动，可以临时借清华镜像来升级：

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
```
