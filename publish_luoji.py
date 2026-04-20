#!/usr/bin/env python3
"""
微信公众号发布脚本 - 罗辑思维样式版 v2.0.0

样式特点（参考罗辑思维公众号）：
1. 开头引言块：灰色背景 + 橙色左边线
2. 少量段落标题：只识别显式 ## 标题，不自动识别
3. 重点文字：橙色加粗
4. 整体简洁：段落自然衔接，不碎片化
5. 字体 15px，行高 2
6. 禁止无序/有序列表
"""
import json
import subprocess
import re
import sys

# 微信API配置
WX_APPID = "wx4a6686caee9e8116"
WX_SECRET = "bb47c0cdbf6c46c598c15280dd4f2ef9"
WENYAN_BIN = "/Users/aiven/.npm-global/bin/wenyan"

# 默认封面图
THUMB_MEDIA_ID = "rRdlQ0gFDUx_rxXZcd7Vh4cgyHLNLqgWfV3_KjsFLstFqZpk2clh1UIjbNSqQmvm"

# 罗辑思维样式配置
ORANGE_COLOR = "#e36c09"
FONT_FAMILY = '-apple-system, BlinkMacSystemFont, "PingFangSC-Light", "PingFang SC", "Microsoft YaHei", sans-serif'

def get_access_token():
    """获取微信 access_token"""
    result = subprocess.run([
        'curl', '-s', 
        f'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={WX_APPID}&secret={WX_SECRET}'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)['access_token']

def download_image(url: str) -> str:
    """从网络URL下载图片到临时文件"""
    import tempfile
    import urllib.request
    import os
    
    # 获取文件扩展名
    ext = '.jpg'
    if '.png' in url.lower():
        ext = '.png'
    elif '.gif' in url.lower():
        ext = '.gif'
    elif '.webp' in url.lower():
        ext = '.webp'
    
    tmp_path = tempfile.mktemp(suffix=ext)
    
    try:
        # 使用 curl 下载
        result = subprocess.run([
            'curl', '-s', '-L', '-o', tmp_path, url
        ], capture_output=True, text=True, timeout=30)
        
        if os.path.exists(tmp_path) and os.path.getsize(tmp_path) > 1000:
            print(f"✅ 图片下载成功: {tmp_path}")
            return tmp_path
        else:
            print(f"⚠️ 图片下载失败，使用默认封面")
            return None
    except Exception as e:
        print(f"⚠️ 下载异常: {e}")
        return None

def compress_image(input_path: str) -> str:
    """压缩图片到 64KB 以下，使用Pillow智能压缩保持最佳清晰度"""
    import os
    import tempfile
    from PIL import Image
    
    tmp_path = tempfile.mktemp(suffix='.jpg')
    
    # 微信封面标准尺寸：900x383 (2.35:1)
    target_width = 900
    target_height = 383
    
    # 使用Pillow打开并resize（高质量插值）
    img = Image.open(input_path)
    
    # 转换为RGB模式（JPEG需要）
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    # 使用高质量 Lanczos 插值 resize
    img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # 智能压缩：逐步降低质量直到满足大小要求
    for quality in [95, 90, 85, 80, 75, 70, 65, 60, 55, 50]:
        img.save(tmp_path, 'JPEG', quality=quality, optimize=True)
        size_kb = os.path.getsize(tmp_path) / 1024
        if size_kb <= 64:
            break
    
    return tmp_path

def upload_thumb_image(image_path: str, token: str) -> str:
    """上传封面图并返回永久素材 media_id"""
    import os
    
    # 如果是网络URL，先下载
    if image_path.startswith('http://') or image_path.startswith('https://'):
        print(f"🌐 检测到网络图片，正在下载...")
        local_path = download_image(image_path)
        if local_path:
            image_path = local_path
        else:
            return THUMB_MEDIA_ID
    
    # 压缩图片到 64KB 以下（保持最佳清晰度）
    print(f"🖼️ 正在优化图片...")
    tmp_path = compress_image(image_path)
    print(f"✅ 图片压缩完成，大小: {os.path.getsize(tmp_path)/1024:.1f}KB")
    
    try:
        # 使用永久素材接口上传
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            f'https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={token}&type=image',
            '-F', f'media=@{tmp_path}'
        ], capture_output=True, text=True)
        
        resp = json.loads(result.stdout)
        if 'media_id' in resp:
            print(f"✅ 封面上传成功: {resp['media_id']}")
            return resp['media_id']
        else:
            print(f"⚠️ 封面上传失败: {resp}")
            return THUMB_MEDIA_ID
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def process_inline_formatting(text: str) -> str:
    """处理行内格式：加粗、重点"""
    # 重点文字：橙色加粗 **文字**
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong style="color:#e36c09;font-weight:bold;">\1</strong>', text)
    # 斜体 *文字*
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    return text

def render_md_to_html_luoji(md_file: str, title: str, author: str = "小北Aiven", skip_cover: bool = True) -> str:
    """
    解析 MD 文件，构建罗辑思维样式 HTML v2.0.0
    
    核心变化：
    - 不自动识别段落标题，只处理显式 ## 标题
    - 开头段落用引言块样式（灰色背景+橙色左边线）
    - 整体简洁，段落自然衔接
    """
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    html_parts = []
    
    # 正文解析
    lines = content.split('\n')
    
    # 收集所有段落
    paragraphs = []
    current_lines = []
    
    for line in lines:
        line = line.rstrip()
        if line.strip():
            current_lines.append(line)
        else:
            if current_lines:
                paragraphs.append('\n'.join(current_lines))
                current_lines = []
    
    if current_lines:
        paragraphs.append('\n'.join(current_lines))
    
    # 处理段落
    for idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
        
        # === 显式 Markdown 标题：## ===
        if para.startswith('## '):
            title_text = para[3:].strip()
            title_text = process_inline_formatting(title_text)
            html_parts.append(f'''<div style="margin:40px 0 30px 0;">
    <p style="font-size:19px;font-weight:bold;color:#1a1a1a;border-left:5px solid {ORANGE_COLOR};padding-left:14px;margin:0;line-height:1.7;">{title_text}</p>
</div>''')
            continue
        
        # === 引用块 ===
        if para.startswith('> '):
            quote_text = para[2:].strip()
            quote_text = process_inline_formatting(quote_text)
            html_parts.append(f'''<blockquote style="background:#f2f2f2;border-left:5px solid {ORANGE_COLOR};padding:16px 20px;margin:28px 0;font-size:15px;color:#333;line-height:2;text-align:justify;">{quote_text}</blockquote>''')
            continue
        
        # === 开头段落：用引言块样式 ===
        if idx == 0:
            # 第一段用引言块样式
            processed = process_inline_formatting(para)
            html_parts.append(f'''<blockquote style="background:#f2f2f2;border-left:5px solid {ORANGE_COLOR};padding:16px 20px;margin:28px 0;font-size:15px;color:#333;line-height:2;text-align:justify;">{processed}</blockquote>''')
            continue
        
        # === 普通段落 ===
        processed = process_inline_formatting(para)
        html_parts.append(f'<p style="margin:24px 0;line-height:2;color:#333;font-size:15px;text-align:justify;">{processed}</p>')
    
    # === 固定结尾引导 ===
    ending_html = '''
<div style="text-align:center;padding:35px 25px;background:#f9f9f9;border-radius:8px;margin-top:45px;">
    <p style="color:#666;font-size:15px;line-height:2.2;margin:0 0 12px 0;"><strong>谢谢你看到这里~~</strong></p>
    <p style="color:#666;font-size:14px;line-height:2;margin:0 0 12px 0;">这里不只聊 AI，也陪你一起慢慢成长。</p>
    <p style="color:#666;font-size:14px;line-height:2;margin:0 0 12px 0;"><strong>如果今天的内容对你有启发，欢迎点赞、在看、转发三连支持～</strong></p>
    <p style="color:#666;font-size:14px;line-height:2;margin:0 0 12px 0;">怕错过更新？记得点击「小北学 AI」名片，设为星标⭐，我们下次准时相见。</p>
    <p style="color:#666;font-size:14px;line-height:2;margin:0 0 12px 0;"><strong>愿我们眼里有光，心中有方向，在 AI 与成长的路上，一路同行。</strong></p>
    <p style="color:#888;font-size:12px;line-height:1.8;margin:12px 0 0 0;">/ 作者：小北Aiven</p>
    <p style="color:#888;font-size:12px;line-height:1.8;margin:0;">/ 交流合作可联系邮箱：tong1025619710@126.com</p>
</div>'''
    html_parts.append(ending_html)
    
    # 组装完整HTML
    full_html = f'''<section style="font-family:{FONT_FAMILY};line-height:2;font-size:15px;color:#333;padding:0 5px;">
{''.join(html_parts)}
</section>'''
    
    return full_html

def publish(title: str, content: str, author: str = "小北Aiven", thumb_media_id: str = None) -> dict:
    """发布到微信草稿箱"""
    token = get_access_token()
    
    if thumb_media_id and thumb_media_id.startswith('/'):
        print(f"📷 正在上传封面图...")
        thumb_media_id = upload_thumb_image(thumb_media_id, token)
        print(f"📷 封面图 media_id: {thumb_media_id}")
    
    final_thumb = thumb_media_id if thumb_media_id else THUMB_MEDIA_ID
    
    plain_text = re.sub(r'<[^>]+>', '', content).replace('\n', ' ').strip()
    digest = plain_text[:54] + "..." if len(plain_text) > 54 else plain_text
    
    data = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "content_source_url": "",
            "thumb_media_id": final_thumb,
            "need_open_comment": 1,
            "only_fans_can_comment": 0
        }]
    }
    
    with open('/tmp/draft.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    
    result = subprocess.run([
        'curl', '-s', '-X', 'POST',
        f'https://api.weixin.qq.com/cgi-bin/draft/add?access_token={token}',
        '-H', 'Content-Type: application/json; charset=utf-8',
        '--data-binary', '@/tmp/draft.json'
    ], capture_output=True, text=True)
    
    return json.loads(result.stdout)

def main():
    if len(sys.argv) < 3:
        print("用法: python3 publish_luoji.py <md文件> <标题> [作者] [封面图路径]")
        print("")
        print("罗辑思维样式 v2.0.0 特点：")
        print("  - 开头段落：引言块样式（灰色背景+橙色左边线）")
        print("  - 段落标题：只识别显式 ## 标题")
        print("  - 重点文字：橙色加粗")
        print("  - 整体简洁：15px字体，行高2，段落自然衔接")
        sys.exit(1)
    
    md_file = sys.argv[1]
    title = sys.argv[2]
    author = sys.argv[3] if len(sys.argv) > 3 else "小北Aiven"
    thumb_path = sys.argv[4] if len(sys.argv) > 4 else None
    
    print(f"📝 正在渲染: {md_file}")
    print(f"📌 标题: {title}")
    print(f"🎨 应用样式: 罗辑思维风格 v2.0.0")
    
    html = render_md_to_html_luoji(md_file, title, author, skip_cover=True)
    
    print(f"✅ HTML生成完成")
    
    print(f"📤 正在发布到微信...")
    result = publish(title, html, author, thumb_path)
    
    if 'media_id' in result:
        print(f"✅ 发布成功! Media ID: {result['media_id']}")
    else:
        print(f"❌ 发布失败: {result}")

if __name__ == '__main__':
    main()
