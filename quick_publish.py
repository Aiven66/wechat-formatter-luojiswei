#!/usr/bin/env python3
"""
🚀 GitHub 一键发布工具 - 引导用户获取 Token 并发布

使用方法（复制粘贴整个命令）：
python3 -c "
import urllib.request,os,json
token=input('请粘贴你的 GitHub Personal Access Token: ').strip()
if not token: print('Token 不能为空'); exit(1)
req=urllib.request.Request('https://api.github.com/user',headers={'Authorization':f'Bearer {token}','Accept':'application/vnd.github+json','User-Agent':'publisher'})
try:
    with urllib.request.urlopen(req) as r: me=json.loads(r.read()); print(f'✅ 验证成功: @{me[\"login\"]}')
except Exception as e: print(f'❌ Token 无效: {e}'); exit(1)
exec(urllib.request.urlopen(urllib.request.Request('https://raw.githubusercontent.com/Aiven66/wechat-formatter-luojiswei/main/github_publish.py',headers={'User-Agent':'publisher'})).read())
"
"""

import os, sys, base64, json, urllib.request, urllib.error, getpass

REPO_NAME = "wechat-formatter-luojiswei"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_USER = "Aiven66"
DESCRIPTION = "微信公众号排版工具 · 罗辑思维风格 — 让文章读起来更舒服，写起来更专注。"

def api(method, path, token, data=None):
    url = f"https://api.github.com{path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "wechat-formatter-publisher/1.0"
    }
    body = json.dumps(data).encode() if data else None
    if body:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()), resp.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def file_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_sha(path, token):
    _, status = api("GET", f"/repos/{GITHUB_USER}/{REPO_NAME}/contents/{path}", token)
    if status == 200:
        return _.get("sha")
    return None

def main():
    if len(sys.argv) < 2:
        print("❌ 请提供 GitHub Token")
        print()
        print("📋 Token 获取步骤：")
        print("  1. 打开 → https://github.com/settings/tokens")
        print("  2. 点击 'Generate new token (classic)'")
        print("  3. Note 填: 'wechat-formatter-publisher'")
        print("  4. 勾选权限: ✅ repo (全部)")
        print("  5. 点击 'Generate token'")
        print("  6. 复制 Token，粘贴到下方")
        print()
        token = getpass.getpass("粘贴 GitHub Token: ").strip()
        if not token:
            print("Token 不能为空")
            sys.exit(1)
    else:
        token = sys.argv[1].strip()

    # 验证 token
    print("\n🔑 验证 Token...")
    user_data, status = api("GET", "/user", token)
    if status != 200:
        print(f"❌ Token 无效 (status: {status})")
        print(f"   {user_data.get('message', '')}")
        sys.exit(1)
    print(f"   ✅ 验证成功: @{user_data['login']}")

    print("\n" + "=" * 50)
    print("  wechat-formatter-luojiswei GitHub 发布")
    print("=" * 50)

    # Step 1: 创建仓库
    print("\n📦 创建 GitHub 仓库...")
    payload = {
        "name": REPO_NAME,
        "description": DESCRIPTION,
        "public": True,
        "auto_init": False
    }
    _, status = api("POST", f"/user/repos", token, payload)
    if status == 201:
        print("   ✅ 仓库创建成功")
    elif status == 422:
        print("   ⚠️ 仓库已存在，跳过创建")
    else:
        print(f"   ⚠️ 创建返回 {status}，继续推送文件...")

    # Step 2: 推送文件
    print("\n📤 推送文件...")
    pushed = skipped = 0

    SKIP_PATTERNS = ['__pycache__', '.git', 'gh_bin', 'node_modules']
    SKIP_FILES = ['.DS_Store']

    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if not any(p in d for p in SKIP_PATTERNS)]
        for filename in files:
            if any(f in filename for f in SKIP_FILES):
                skipped += 1
                continue
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, REPO_DIR).replace("\\", "/")

            # 只保留核心文件
            if not any([
                filename == 'README.md',
                filename == 'SKILL.md',
                filename == 'LICENSE',
                filename == 'github_publish.py',
                filename == 'publish_luoji.py',
                filename == 'publish_no_hr.py',
                filename == 'formatter.py',
                filename == 'init.sh',
                'examples/' in relpath or relpath.startswith('examples/'),
                relpath.startswith('assets/'),
            ]):
                skipped += 1
                continue

            content_b64 = file_base64(filepath)
            sha = get_sha(relpath, token)
            msg = f"Upload {relpath}" + (" (update)" if sha else "")

            payload = {"message": msg, "content": content_b64}
            if sha:
                payload["sha"] = sha

            _, status = api("PUT", f"/repos/{GITHUB_USER}/{REPO_NAME}/contents/{relpath}", token, payload)
            if status in [200, 201]:
                action = "✅" if "update" not in msg else "🔄"
                print(f"   {action} {relpath}")
                pushed += 1
            else:
                print(f"   ❌ {relpath} ({status})")
                skipped += 1

    print(f"\n   已推送: {pushed} | 跳过: {skipped}")

    print("\n" + "=" * 50)
    print("  🎉 发布完成！")
    print("=" * 50)
    print(f"\n  📎 仓库地址: https://github.com/{GITHUB_USER}/{REPO_NAME}")
    print(f"  📎 Clone:    git clone https://github.com/{GITHUB_USER}/{REPO_NAME}.git")

if __name__ == "__main__":
    main()
