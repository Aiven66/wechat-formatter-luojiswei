#!/usr/bin/env python3
"""
GitHub Publisher for wechat-formatter-luojiswei
用法: python3 github_publish.py <GITHUB_TOKEN>
"""
import os, sys, base64, json, urllib.request, urllib.error

REPO_NAME = "wechat-formatter-luojiswei"
REPO_DIR = os.path.dirname(os.path.abspath(__file__))
GITHUB_USER = "Aiven66"
DESCRIPTION = "微信公众号排版工具 · 罗辑思维风格 — 让文章读起来更舒服，写起来更专注。"

def api(method, path, token, data=None):
    """GitHub REST API 调用"""
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

def main():
    if len(sys.argv) < 2:
        print("❌ 请提供 GitHub Token")
        print()
        print("用法: python3 github_publish.py <GITHUB_TOKEN>")
        print()
        print("获取 Token 方法:")
        print("  1. 打开 https://github.com/settings/tokens")
        print("  2. 点击 'Generate new token (classic)'")
        print("  3. 设置名称，选择 'repo' 权限")
        print("  4. 点击 Generate，复制 token 粘贴过来")
        print()
        print("一次性命令:")
        print("  python3 github_publish.py ghp_xxxxxxxxxxxx")
        sys.exit(1)

    token = sys.argv[1].strip()

    print("=" * 50)
    print("  wechat-formatter-luojiswei GitHub 发布")
    print("=" * 50)

    # Step 1: 创建仓库
    print("\n📦 创建 GitHub 仓库...")
    payload = {
        "name": REPO_NAME,
        "description": DESCRIPTION,
        "public": True,
        "auto_init": False,
        "delete_branch_on_merge": False
    }
    _, status = api("POST", "/orgs/Aiven66/repos", token, payload)
    if status == 201:
        print("  ✅ 仓库创建成功")
    elif status == 422:
        # 仓库已存在，获取之
        print("  ⚠️ 仓库已存在，跳过创建")
    else:
        print(f"  ❌ 创建失败 (status: {status})，尝试推送文件...")

    # Step 2: 推送文件
    print("\n📤 推送文件...")
    sha_cache = {}

    def get_sha(path):
        if path in sha_cache:
            return sha_cache[path]
        _, status = api("GET", f"/repos/{GITHUB_USER}/{REPO_NAME}/contents/{path}", token)
        if status == 200:
            return _.get("sha")
        return None

    pushed = 0
    skipped = 0

    for root, dirs, files in os.walk(REPO_DIR):
        # 跳过 .git 等目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'gh_bin']]
        for filename in files:
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, REPO_DIR)

            # 跳过不需要的文件
            skip_ext = ['.pyc', '.local.html', '.wechat.html', '.DS_Store']
            if any(ext in filepath for ext in ['__pycache__', '.git', 'node_modules']):
                skipped += 1
                continue
            if filename.endswith('.md') and 'examples' not in relpath and filename not in ['README.md', 'SKILL.md', 'LICENSE']:
                skipped += 1
                continue

            # 计算 relative path
            repo_rel = relpath.replace('\\', '/')

            # 获取现有 sha（如果文件已存在）
            sha = get_sha(repo_rel)

            # Base64 编码内容
            content_b64 = file_base64(filepath)

            payload = {
                "message": f"Upload {repo_rel}",
                "content": content_b64
            }
            if sha:
                payload["sha"] = sha

            method = "PUT"
            path = f"/repos/{GITHUB_USER}/{REPO_NAME}/contents/{repo_rel}"

            result, status = api(method, path, token, payload)
            if status in [200, 201]:
                print(f"  ✅ {repo_rel}")
                pushed += 1
            elif status == 415:
                print(f"  ⚠️ 跳过（二进制）: {repo_rel}")
                skipped += 1
            else:
                print(f"  ❌ {repo_rel} (status: {status})")
                try:
                    print(f"     {result.get('message', '')}")
                except:
                    pass

    print(f"\n  已推送: {pushed} 文件， 跳过: {skipped} 文件")

    print("\n" + "=" * 50)
    print("  🎉 发布完成！")
    print("=" * 50)
    print()
    print(f"  📎 仓库地址: https://github.com/{GITHUB_USER}/{REPO_NAME}")
    print(f"  📎 Clone:    git clone https://github.com/{GITHUB_USER}/{REPO_NAME}.git")

if __name__ == "__main__":
    main()
