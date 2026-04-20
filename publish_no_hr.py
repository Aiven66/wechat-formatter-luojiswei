#!/usr/bin/env python3
"""
微信公众号发布脚本 - 禁用间隔线版
使用方法: python3 publish_no_hr.py <md文件> <标题> [作者]
"""
import json
import subprocess
import re
import sys

WENYAN_BIN = "/Users/aiven/.npm-global/bin/wenyan"
CUSTOM_CSS = "/Users/aiven/.wenyan-themes/luojiswei-no-hr.css"
THUMB_MEDIA_ID = "rRdlQ0gFDUx_rxXZcd7Vh4cgyHLNLqgWfV3_KjsFLstFqZpk2clh1UIjbNSqQmvm"

def get_access_token():
    """获取微信 access_token"""
    result = subprocess.run([
        'curl', '-s', 
        'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wx4a6686caee9e8116&secret=bb47c0cdbf6c46c598c15280dd4f2ef9'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)['access_token']

def render_md_no_hr(md_file: str) -> str:
    """渲染MD并移除所有hr标签"""
    # 渲染MD
    result = subprocess.run([
        WENYAN_BIN, "render", "-f", md_file,
        "--custom-theme", CUSTOM_CSS
    ], capture_output=True, text=True)
    
    html = result.stdout
    
    # 删除所有 hr 标签（CSSL display:none 在微信不生效）
    html = re.sub(r'<hr[^>]*/?>', '', html)
    html = re.sub(r'</hr>', '', html)
    
    return html

def extract_body(html: str) -> str:
    """提取 wenyan section 内的 body 内容"""
    body_match = re.search(r'<section id="wenyan"[^>]*>(.*?)</section>', html, re.DOTALL)
    return body_match.group(1) if body_match else html

def publish(title: str, content: str, author: str = "小北Aiven") -> dict:
    """发布到微信草稿箱"""
    token = get_access_token()
    
    data = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": content[:100] + "..." if len(content) > 100 else content,
            "content": content,
            "content_source_url": "",
            "thumb_media_id": THUMB_MEDIA_ID,
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
        print("用法: python3 publish_no_hr.py <md文件> <标题> [作者]")
        sys.exit(1)
    
    md_file = sys.argv[1]
    title = sys.argv[2]
    author = sys.argv[3] if len(sys.argv) > 3 else "小北Aiven"
    
    print(f"📝 正在渲染: {md_file}")
    html = render_md_no_hr(md_file)
    
    print(f"🔍 提取正文内容...")
    body = extract_body(html)
    
    # 检查是否还有 hr
    hr_count = len(re.findall(r'<hr', body))
    if hr_count > 0:
        print(f"⚠️ 警告: 仍有 {hr_count} 个 hr 标签")
    else:
        print(f"✅ 已清除所有 hr 标签")
    
    print(f"📤 正在发布到微信...")
    result = publish(title, body, author)
    
    if 'media_id' in result:
        print(f"✅ 发布成功! Media ID: {result['media_id']}")
    else:
        print(f"❌ 发布失败: {result}")

if __name__ == '__main__':
    main()
