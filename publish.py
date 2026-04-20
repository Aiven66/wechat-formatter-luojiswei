#!/usr/bin/env python3
"""
🚀 GitHub Publisher - PyGithub 版本
自动创建仓库 + 推送全部文件

使用方法:
  python3 publish.py <GITHUB_TOKEN>

Token 获取: https://github.com/settings/tokens
  → Generate new token (classic)
  → 勾选: ✅ repo (全部)
  → Generate
"""
import os, sys, base64
from github import Github

REPO_NAME = "wechat-formatter-luojiswei"
REPO_DIR = os.path.dirname(os.path.abspath(__file__)) or "."
GITHUB_USER = "Aiven66"
DESCRIPTION = "微信公众号排版工具 · 罗辑思维风格 — 让文章读起来更舒服，写起来更专注。"

# 要跳过的文件
SKIP_PATTERNS = ['__pycache__', '.git', 'gh_bin', 'node_modules', '.DS_Store', '.local.html', '.wechat.html']
# 只保留这些文件（None = 全部）
ALLOWED = {
    'README.md', 'SKILL.md', 'LICENSE', 'publish_luoji.py', 'publish_no_hr.py',
    'formatter.py', 'init.sh', 'github_publish.py', 'quick_publish.py',
    'publish.py'
}

def main():
    # 获取 token
    if len(sys.argv) < 2:
        import getpass
        print("=" * 54)
        print("  🚀 wechat-formatter-luojiswei GitHub 发布工具")
        print("=" * 54)
        print()
        print("📋 Token 获取步骤:")
        print("  1. 打开 → https://github.com/settings/tokens")
        print("  2. 点击 'Generate new token (classic)'")
        print("  3. Note 填: 'wechat-publisher'")
        print("  4. 勾选: ✅ repo (全部 repo 权限)")
        print("  5. 点击 Generate，复制 Token 粘贴到下方")
        print()
        token = getpass.getpass("📎 粘贴 GitHub Token: ").strip()
        if not token:
            print("❌ Token 不能为空"); sys.exit(1)
    else:
        token = sys.argv[1].strip()

    # 连接 GitHub
    print("\n🔑 连接 GitHub...")
    g = Github(token)
    try:
        user = g.get_user()
        login = user.login
        print(f"   ✅ 登录成功: @{login}")
    except Exception as e:
        print(f"❌ 认证失败: {e}")
        sys.exit(1)

    print("\n" + "=" * 54)
    print(f"  发布 → {REPO_NAME}")
    print("=" * 54)

    # Step 1: 创建仓库
    print("\n📦 创建仓库...")
    try:
        repo = user.create_repo(
            name=REPO_NAME,
            description=DESCRIPTION,
            private=False,
            auto_init=False,
            delete_branch_on_merge=False
        )
        print(f"   ✅ 仓库创建成功!")
    except Exception as e:
        if "already exists" in str(e).lower() or "422" in str(e):
            print("   ⚠️ 仓库已存在，跳过创建")
            repo = g.get_repo(f"{login}/{REPO_NAME}")
        else:
            print(f"   ❌ 创建失败: {e}")
            sys.exit(1)

    # Step 2: 收集文件
    print("\n📂 收集文件...")
    files_to_push = []
    for root, dirs, files in os.walk(REPO_DIR):
        dirs[:] = [d for d in dirs if not any(p in d for p in SKIP_PATTERNS)]
        for filename in files:
            if any(p in filename for p in SKIP_PATTERNS):
                continue
            filepath = os.path.join(root, filename)
            relpath = os.path.relpath(filepath, REPO_DIR).replace("\\", "/")
            if ALLOWED and filename not in ALLOWED and not filename.startswith('example-'):
                continue
            files_to_push.append((relpath, filepath))

    print(f"   找到 {len(files_to_push)} 个文件")

    # Step 3: 推送文件
    print("\n📤 推送文件...")
    pushed = skipped = 0

    for relpath, filepath in sorted(files_to_push):
        with open(filepath, 'rb') as f:
            content = f.read()

        try:
            # 尝试获取现有文件 SHA
            try:
                existing = repo.get_contents(relpath)
                sha = existing.sha
                msg = f"docs: update {relpath}"
            except Exception:
                sha = None
                msg = f"docs: add {relpath}"

            # 创建/更新文件
            if sha:
                repo.update_file(relpath, msg, content, sha)
                print(f"   🔄 {relpath}")
            else:
                repo.create_file(relpath, msg, content)
                print(f"   ✅ {relpath}")
            pushed += 1
        except Exception as e:
            print(f"   ❌ {relpath}: {e}")
            skipped += 1

    print(f"\n   已推送: {pushed} | 失败: {skipped}")

    print("\n" + "=" * 54)
    print("  🎉 发布完成!")
    print("=" * 54)
    url = f"https://github.com/{login}/{REPO_NAME}"
    print(f"\n  📎 仓库: {url}")
    print(f"  📎 Clone: git clone https://github.com/{login}/{REPO_NAME}.git")
    print(f"\n  📎 Skill 安装: skillshub install wechat-formatter-luojiswei@{GITHUB_USER}")
    print(f"     或访问: {url}")

if __name__ == "__main__":
    main()
