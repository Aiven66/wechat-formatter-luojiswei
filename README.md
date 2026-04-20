# wechat-formatter-luojiswei

> 微信公众号排版工具 · 罗辑思维风格 — 让文章读起来更舒服，写起来更专注。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-green.svg)](https://www.python.org/)

---

## ✨ 特性

- **罗辑思维风格排版**：简洁、少标题、自然段落、无分隔线
- **智能标题识别**：仅识别显式 `##` 标题，段落标题蓝色左边线
- **重点文字高亮**：橙色 `#e36c09` + 加粗
- **引言块样式**：灰色背景 + 橙色左边线
- **一键发布**：排版 + 封面图压缩上传 + 推送微信草稿箱
- **零依赖外部服务**：纯 Python 实现

---

## 📦 安装

```bash
# 克隆仓库
git clone https://github.com/Aiven66/wechat-formatter-luojiswei.git
cd wechat-formatter-luojiswei

# 安装依赖
pip install requests Pillow markdown
```

---

## 🚀 快速开始

### 方式一：排版 + 发布（推荐）

```bash
python3 publish_luoji.py <文章.md> <标题> [作者] [封面图路径]
```

**示例：**

```bash
python3 publish_luoji.py my-article.md "我的第一篇文章" "小北Aiven" cover.jpg
```

### 方式二：仅排版

```bash
python3 formatter.py <输入.md> <输出.html>
```

---

## 📝 文章格式规范

### Markdown 写作规范

```markdown
# 封面标题（仅用于生成封面图提示词）

> 引言块：灰色背景 + 橙色左边线，自动识别文件中的引言块

正文内容。写作时尽量用自然段落，避免短句堆砌。

## 01 段落标题（一级段落标题，蓝色左边线）

正文内容。重点文字用 **加粗** 标记，会自动渲染为橙色高亮。

## 02 第二个段落标题

继续正文。
```

### ⚠️ 禁止使用的格式

| 禁止项 | 说明 |
|--------|------|
| `---` 分隔线 | 不渲染，浪费 token |
| 无序列表 `-` | 微信兼容性差 |
| 有序列表 `1.` | 微信兼容性差 |
| 复杂表格 | 微信不支持 markdown 表格 |
| 框线/表格等排版 | 仅使用段落标题 + 正文 |

### 标题装饰符说明

工具**仅识别**以下格式的标题：

```markdown
## 01 标题文字        ← 识别（阿拉伯数字 + 空格）
## 【标题】            ← 识别（中括号）
## 标题               ← 识别（纯文字）
```

其他符号如 `◆`、`▸`、`🟦`、`###` 都不识别为段落标题，仅作为普通文字渲染。

---

## 🎨 排版效果预览

### 封面标题样式
蓝色科技风色块标题，醒目大气

### 段落标题样式
蓝色 `#1890ff` 左边线 + 字号 18px + 加粗

### 引言块样式
- 背景色：`#f5f5f5`（浅灰）
- 左边线：`3px solid #e36c09`（橙色）
- 圆角：`4px`

### 重点文字样式
- 颜色：`#e36c09`（橙色）
- 字重：加粗

---

## 🖼️ 封面图规范

| 参数 | 值 |
|------|------|
| 尺寸 | 900 × 383（2.35:1 横幅） |
| 大小 | ≤ 64KB（微信限制） |
| 格式 | JPG/PNG |
| 来源 | 优先真实图片 > AI 生图 |

### 推荐图片网站

- [Unsplash](https://unsplash.com) — 免费高清，搜索英文关键词
- [Pexels](https://pexels.com) — 同上，中文支持更好
- AI 生图：MiniMax / Midjourney / Stable Diffusion

---

## 📁 目录结构

```
wechat-formatter-luojiswei/
├── SKILL.md              # 技能定义文档
├── README.md             # 本文件
├── LICENSE               # MIT 许可证
├── formatter.py          # 核心排版引擎
├── publish_luoji.py      # 排版 + 微信发布脚本
├── publish_no_hr.py      # 同上（禁止分隔线版本）
├── examples/             # 示例文章
│   └── example.md
└── assets/               # 资源文件（封面图示例）
```

---

## ⚙️ 配置说明

### 微信公众平台 API

发布脚本需要以下配置（在脚本内修改）：

```python
# publish_luoji.py 中的配置项
APPID = "your_appid"           # 微信公众号 appid
APPSECRET = "your_appsecret"   # 微信公众号 appsecret
AUTHOR = "小北Aiven"             # 默认作者名
```

获取方式：[微信公众平台](https://mp.weixin.qq.com) → 设置与开发 → 基本配置

### 环境要求

- Python 3.10+
- requests
- Pillow
- markdown

---

## 🔧 常见问题

### Q: 封面图上传失败？
**A:** 确保图片大小 ≤ 64KB，可使用 `PIL` 压缩：

```python
from PIL import Image
Image.open("cover.jpg").save("cover_compressed.jpg", quality=85, optimize=True)
```

### Q: 分隔线不显示？
**A:** 微信不支持 `---`，本工具已禁用。如需分隔，请用空白行代替。

### Q: 如何添加正文配图？
**A:** 需要先通过微信永久素材接口上传图片，获取 `media_id`，再以 `##media_id##` 格式嵌入文章。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。

---

## 👤 作者

**小北Aiven** — [GitHub](https://github.com/Aiven66)

一个懂点技术喜欢分享的 AI 产品经理，公众号「小北学AI」主理人。

> 如果你觉得这篇文章有帮助，欢迎关注「小北Aiven」，点赞并分享给更多朋友。
