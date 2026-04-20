---
slug: wechat-formatter-luojiswei
displayName: 微信公众号排版（罗辑思维风格）
name: wechat-formatter-luojiswei
version: 2.3.1
summary: 微信公众号 Markdown 转微信 HTML，支持罗辑思维风格排版、一键发布草稿箱。
description: 微信公众号 Markdown 转微信 HTML，支持罗辑思维风格排版、一键发布草稿箱。自动识别 ## 标题、> 引言块、**加粗**，输出微信友好 HTML。
tags:
  - 微信公众号
  - 微信排版
  - Markdown
  - 罗辑思维
  - 内容创作
---

## 使用方法

```bash
# 排版 + 发布到微信草稿箱
python3 publish_luoji.py <文章.md> <标题> [作者] [封面图]

# 仅排版，不发布
python3 formatter.py <输入.md> <输出.html>
```

## 排版规则

| 元素 | 原文写法 | 渲染效果 |
|------|----------|----------|
| 段落标题 | `## 01 标题` | 蓝色左边线，18px 加粗 |
| 引言块 | `> 文字` | 灰色背景，橙色左边线 |
| 重点文字 | `**文字**` | 橙色 #e36c09 加粗 |
| 正文 | 自然段落 | 15px，行高 2.0 |

## 禁止格式

- ❌ `---` 分隔线（不渲染）
- ❌ `-` 无序列表
- ❌ `1.` 有序列表
- ❌ 复杂表格

## 配置

在 `publish_luoji.py` 顶部修改：

```python
APPID = "your_appid"
APPSECRET = "your_appsecret"
AUTHOR = "小北Aiven"
```
