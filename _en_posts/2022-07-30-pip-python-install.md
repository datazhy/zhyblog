---
layout:       post
title:        "How to Speed Up pip Package Downloads"
subtitle:     "Use Reliable PyPI Mirrors in China for Faster Python Package Installation"
description:  "If pip downloads from PyPI are slow or time out, switch to a reliable mirror from Tsinghua University, Alibaba Cloud, Tencent Cloud, or another provider. This guide covers temporary and permanent configuration on Windows, macOS, and Linux."
date:         2022-07-30 12:00:00 +0800
author:       "Zhy"
catalog:      true
header-style: text
lang:         en
permalink:    /en/2022/07/30/pip-python-install/
translation_url: /2022/07/30/pip-python-install/
tags:
    - Python
    - pip
---

## **Introduction**

One reason Python is so useful and widely loved is its rich ecosystem of high-quality third-party packages. Common examples include `requests` for web scraping, `pandas` for data analysis, and `scikit-learn` for machine learning.

* pandas
* numpy
* matplotlib
* scipy
* scikit-learn
* ...

Upgrade pip itself:

```bash
pip install pip -U
```

Install a third-party package:

```bash
pip install pandas
```

Upgrade an installed package:

```bash
pip install --upgrade pandas
```

The problem is that downloads from the default PyPI servers outside mainland China can be slow and may time out. The simplest solution is to use a domestic PyPI mirror.

## **PyPI Mirrors in China**

These mainstream mirrors are actively maintained. Tsinghua University and Alibaba Cloud are good first choices:

```text
Tsinghua University: https://pypi.tuna.tsinghua.edu.cn/simple
Alibaba Cloud:       https://mirrors.aliyun.com/pypi/simple/
Tencent Cloud:       https://mirrors.cloud.tencent.com/pypi/simple/
Huawei Cloud:        https://repo.huaweicloud.com/repository/pypi/simple/
USTC:                https://pypi.mirrors.ustc.edu.cn/simple/
```

> Older mirrors once recommended by Douban, Huazhong University of Science and Technology, and Shandong University of Technology have largely been discontinued or unavailable for long periods, so I do not recommend them. Mirrors can also lag behind PyPI. If a newly released package version is not available yet, temporarily switch back to the official index at `https://pypi.org/simple`.

### **Temporary Use**

Use `-i` to specify a mirror for one command:

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple some-package
```

### **Set a Permanent Default**

Upgrade to a recent version of pip (10.0.0 or later), then set the default index:

```bash
pip install pip -U
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

After the command succeeds, pip writes the setting to its configuration file. The location depends on the operating system:

| System | Configuration file |
| --- | --- |
| Windows | `%APPDATA%\pip\pip.ini` (older versions may use `C:\Users\your-username\pip\pip.ini`) |
| macOS | `~/.config/pip/pip.conf` (or `~/.pip/pip.conf`) |
| Linux | `~/.config/pip/pip.conf` (or `~/.pip/pip.conf`) |

On Windows, the generated `pip.ini` looks like this:

![Automatically generated pip.ini file in the Windows user directory](/img/in-post/pip-install.png)

Its contents are approximately:

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

> The hostname in `trusted-host` must match the hostname in `index-url`. `trusted-host` skips SSL verification for non-HTTPS sources. Because the Tsinghua mirror above uses HTTPS, this setting is usually unnecessary. Add it only when using an HTTP source or troubleshooting an SSL error, and always use the matching hostname.

### **Upgrade pip Through a Mirror**

If the default connection is too slow even to upgrade pip, use the Tsinghua mirror for that command:

```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pip -U
```
