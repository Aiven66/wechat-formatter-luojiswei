#!/usr/bin/env python3
"""
罗辑思维风格排版器
基于罗辑思维公众号文章排版特征
"""

import re
import sys
import json
from pathlib import Path

# 罗辑思维排版配置
CONFIG = {
    'title_color': '#1a1a1a',       # 标题颜色
    'text_color': '#333',           # 正文颜色
    'accent_color': '#E36C09',      # 橙色强调色
    'quote_bg': '#f5f5f5',          # 引言背景
    'quote_color': '#666',          # 引言文字颜色
    'font_family': '-apple-system, BlinkMacSystemFont, "PingFangSC-Light", "PingFang SC", "Microsoft YaHei", sans-serif',
    'font_size': '16px',
    'line_height': '1.9',
    'author': '罗辑思维'
}

def format_luojiswei(content: str, title: str = '', author: str = None) -> str:
    """罗辑思维风格排版"""
    
    if author is None:
        author = CONFIG['author']
    
    parts = []
    
    # 封面标题区
    if title:
        parts.append(f'''
<div style="text-align:center;padding:30px 20px 25px;border-bottom:1px solid #f0f0f0;">
    <h1 style="font-size:24px;font-weight:bold;color:{CONFIG['title_color']};margin:0 0 12px;line-height:1.4;">「{title}」</h1>
    <p style="font-size:13px;color:#999;margin:0;">{author}</p>
</div>
''')
    
    # 内容处理
    lines = content.strip().split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # 一级标题 ## xxx
        if line.startswith('## '):
            title_text = line[3:].strip()
            parts.append(f'<p style="font-size:19px;font-weight:bold;color:{CONFIG["title_color"]};padding-left:15px;border-left:4px solid {CONFIG["accent_color"]};margin:35px 0 20px;">{title_text}</p>')
        
        # 二级标题 ### xxx
        elif line.startswith('### '):
            title_text = line[4:].strip()
            parts.append(f'<p style="font-size:17px;font-weight:bold;color:{CONFIG["text_color"]};padding-left:12px;border-left:3px solid {CONFIG["accent_color"]};margin:28px 0 16px;">{title_text}</p>')
        
        # 三级标题 #### xxx
        elif line.startswith('#### '):
            title_text = line[5:].strip()
            parts.append(f'<p style="font-size:16px;font-weight:bold;color:{CONFIG["text_color"]};margin:24px 0 14px;">{title_text}</p>')
        
        # 引用块 > xxx
        elif line.startswith('> '):
            quote_text = line[2:].strip()
            parts.append(f'<p style="background:{CONFIG["quote_bg"]};border-left:4px solid {CONFIG["accent_color"]};padding:15px 20px;margin:20px 0;font-size:15px;color:{CONFIG["quote_color"]};line-height:1.8;">{quote_text}</p>')
        
        # 无序列表 - xxx
        elif line.startswith('- ') or line.startswith('* '):
            item_text = line[2:].strip()
            parts.append(f'<p style="margin:10px 0 10px 25px;color:{CONFIG["text_color"]};line-height:{CONFIG["line_height"]};">• {item_text}</p>')
        
        # 数字列表 1. xxx
        elif re.match(r'^\d+\.\s', line):
            item_text = re.sub(r'^\d+\.\s+', '', line)
            parts.append(f'<p style="margin:10px 0 10px 25px;color:{CONFIG["text_color"]};line-height:{CONFIG["line_height"]};">{item_text}</p>')
        
        # 普通段落
        else:
            # 处理行内格式
            formatted = format_inline(line)
            parts.append(f'<p style="margin:16px 0;line-height:{CONFIG["line_height"]};color:{CONFIG["text_color"]};font-size:{CONFIG["font_size"]};">{formatted}</p>')
        
        i += 1
    
    # 结尾引导
    parts.append(f'''
<div style="text-align:center;padding:35px 20px;background:#fafafa;border-radius:10px;margin:35px 20px 0;">
    <p style="color:#666;font-size:14px;line-height:2.2;margin:0;">
        如果你觉得这篇文章有帮助<br>
        欢迎<span style="color:{CONFIG['accent_color']};font-weight:bold;">关注、点赞、分享</span>
    </p>
</div>
''')
    
    return '\n'.join(parts)

def format_inline(text: str) -> str:
    """处理行内格式：加粗、斜体等"""
    # 加粗 **xxx**
    text = re.sub(r'\*\*(.+?)\*\*', f'<strong style="color:{CONFIG["accent_color"]};">\\1</strong>', text)
    # 斜体 *xxx*
    text = re.sub(r'\*(.+?)\*', '<em>\\1</em>', text)
    return text

def wrap_html(body: str, title: str = '') -> str:
    """包装成完整HTML"""
    return f'''<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
</head>
<body style="font-family:{CONFIG['font_family']};line-height:{CONFIG['line_height']};font-size:{CONFIG['font_size']};color:{CONFIG['text_color']};max-width:677px;margin:0 auto;padding:15px 20px;">
{body}
</body>
</html>'''

def main():
    if len(sys.argv) < 2:
        print("用法: python3 luojiswei_formatter.py <markdown文件> [标题] [作者]")
        sys.exit(1)
    
    md_file = Path(sys.argv[1])
    title = sys.argv[2] if len(sys.argv) > 2 else md_file.stem.replace('-', ' ')
    author = sys.argv[3] if len(sys.argv) > 3 else CONFIG['author']
    
    content = md_file.read_text(encoding='utf-8')
    
    # 移除front matter
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            content = parts[2]
    
    body = format_luojiswei(content, title, author)
    html = wrap_html(body, title)
    
    output = md_file.parent / f"{md_file.stem}.luojiswei.html"
    output.write_text(html, encoding='utf-8')
    
    print(f"✓ 罗辑思维风格排版完成: {output}")

if __name__ == '__main__':
    main()
