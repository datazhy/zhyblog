# 写完文章后如何更新到网站

本博客用 **Jekyll** 构建，代码托管在 GitHub（`datazhy/zhyblog`），由 **Cloudflare Pages** 自动部署。

> **核心逻辑一句话**：你只要把写好的文章 `git push` 到 GitHub，Cloudflare 会自动构建并上线，1～2 分钟后 4 个域名（zhy.win / www.zhy.win / zhanghangyu.com / www.zhanghangyu.com）同步更新。**全程不需要手动部署。**

---

## 一、最常用流程（照这个做就行）

### 1. 新建文章文件

在 `_posts/` 目录下新建一个 Markdown 文件，**文件名必须是这个格式**：

```
YYYY-MM-DD-英文标题.md
```

例如：`2026-07-06-my-first-post.md`

- 日期决定文章的发布时间和排序，Jekyll 靠文件名识别文章，**格式错了不会显示**。
- 标题部分用英文/拼音、单词间用连字符 `-`（它会成为文章网址的一部分）。

### 2. 写好开头的 Front Matter（文章配置）

每篇文章开头必须有一段用 `---` 包起来的配置。直接复制下面这段修改即可（也可以复制 `_posts/模板.md`）：

```markdown
---
layout:       post
title:        "文章标题"
subtitle:     "副标题（显示在标题下方）"
description:  "一句话概括本文，用于搜索引擎摘要和分享卡片，建议 60-120 字"
date:         2026-07-06 12:00:00
author:       "Zhy"
catalog:      true
header-style: text
tags:
    - Python
    - 数据分析
---

正文从这里开始，用 Markdown 写……
```

字段说明：

| 字段 | 作用 | 必填 |
|---|---|---|
| `title` | 文章标题 | ✅ |
| `subtitle` | 副标题 | 可选 |
| `description` | 搜索引擎摘要（**对 SEO 很重要，建议填**） | 推荐 |
| `date` | 发布时间 | ✅ |
| `author` | 作者，一般写 `"Zhy"` | 可选 |
| `catalog` | `true` 显示右侧目录 | 可选 |
| `tags` | 标签，每行一个 | 推荐 |

### 3. 插入图片

图片放到 `img/in-post/` 目录，正文里这样引用（**alt 文字别留空，利于 SEO**）：

```markdown
![图片的替代文字](/img/in-post/你的图片.png)
```

### 4. 发布（推送到 GitHub）

在博客目录 `/Users/zhy/Documents/个人博客` 下打开终端，执行：

```bash
git add .
git commit -m "新增文章：文章标题"
git push
```

推送成功后，Cloudflare Pages 会自动开始构建，**约 1～2 分钟后线上生效**。

### 5. 查看效果

打开 https://www.zhy.win 查看。

> ⚠️ **看不到更新？** 本站是 PWA、带 Service Worker 缓存，浏览器可能给你旧页面。按 **`Cmd + Shift + R` 强制刷新**一两次即可。

---

## 二、（可选）发布前本地预览

想在推送前先看看效果，可以在本地跑 Jekyll。**注意本机有两个必须的环境变量前缀**，否则会报错：

```bash
# 进入博客目录
cd /Users/zhy/Documents/个人博客

# 必须带上这两组变量：用 Homebrew 的新版 Ruby + UTF-8 编码（目录含中文）
export PATH="/opt/homebrew/opt/ruby/bin:$PATH"
export LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

# 首次需要先装依赖（只需一次）
bundle install

# 启动本地预览
bundle exec jekyll serve
```

然后浏览器打开 http://localhost:4000 预览。改动会实时重新生成。确认无误后再按「一、第 4 步」推送。

> 为什么要这两个变量：系统自带的 Ruby 2.6 跑不了 Jekyll 4；目录名是中文「个人博客」，不设 UTF-8 会报 `incompatible character encodings` 错误。

---

## 三、常见问题

**Q：文章推送了但网站没更新？**
1. 确认 `git push` 成功（没有报错）。
2. 等 1～2 分钟（Cloudflare 在构建）。
3. 浏览器 `Cmd + Shift + R` 强刷（Service Worker 缓存）。
4. 还不行就去 Cloudflare 后台看构建日志：Workers 和 Pages → `zhyblog` → 部署，看最新一次是否失败。

**Q：文章根本不显示 / 排序不对？**
→ 十有八九是文件名格式不对。必须是 `YYYY-MM-DD-标题.md`，日期要合法。

**Q：想先写草稿、暂不发布？**
→ 在 Front Matter 里加一行 `published: false`，它就不会出现在网站上；想发布时删掉这行或改成 `true`。

**Q：本地用 `curl` 测 zhy.win 结果不对？**
→ 本机开了 WARP，会把 zhy.win 的 DNS 劫持到本地缓存，`curl` 结果不可信。以浏览器实际访问为准（强刷后）。

---

## 四、极简速查

```bash
# 1. 在 _posts/ 建文件： YYYY-MM-DD-title.md，写好 front matter 和正文
# 2. 发布三连：
git add .
git commit -m "新增文章：xxx"
git push
# 3. 等 1-2 分钟，浏览器 Cmd+Shift+R 打开 https://www.zhy.win
```

---

## 附：这套系统长什么样

- **写作**：本地 `_posts/` 目录，Markdown 文件
- **仓库**：GitHub `datazhy/zhyblog`，`main` 分支
- **托管**：Cloudflare Pages 项目 `zhyblog`，监听 `main` 分支，push 即自动构建（`bundle install && bundle exec jekyll build` → `_site`）
- **域名**：zhy.win、www.zhy.win、zhanghangyu.com、www.zhanghangyu.com（都指向 Cloudflare Pages）
- **访客统计**：页脚的访客计数用 Vercount；另有 Umami、Google Analytics 做后台分析
