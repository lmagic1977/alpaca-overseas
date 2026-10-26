# 出海攻略（博客）

每篇文章一个 .md 文件，文件名就是网址：`mx-to-us-visa.md` → https://visas.run/blog/mx-to-us-visa

文件开头写这几行（--- 之间），下面写正文：

```
---
title: 文章标题（会出现在百度/谷歌搜索结果里）
description: 一两句话摘要，80 字左右
keywords: 关键词1,关键词2
date: 2026-10-26
pic: mx-angel2          （tools/images.json 里的图片名）
tag: 墨西哥
service: 墨西哥工签绿卡  （文末“咨询”按钮带上的服务）
---
```

正文支持：`## 小标题`、`### 小小标题`、`- 列表`、`1. 编号列表`、`**加粗**`、`[链接文字](/sg)`、`> 提示框`。
写完跑 `python3 tools/build.py`，文章会自动加进博客列表、首页“出海攻略”和 sitemap.xml。
