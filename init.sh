#!/bin/bash
# wechat-formatter-luojiswei / GitHub 发布脚本
# 运行此脚本，自动完成：初始化 Git → 创建远程仓库 → 推送

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_NAME="wechat-formatter-luojiswei"
GITHUB_USER="Aiven66"

echo "========================================"
echo "  wechat-formatter-luojiswei GitHub 发布"
echo "========================================"
echo ""

# Step 1: 检查 gh CLI
check_gh() {
    if command -v gh &> /dev/null; then
        echo "✅ gh CLI 已安装: $(gh --version | head -1)"
    else
        echo "❌ gh CLI 未安装"
        echo ""
        echo "请选择安装方式："
        echo ""
        echo "  方式A - Homebrew（推荐）:"
        echo "    /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo "    brew install gh"
        echo ""
        echo "  方式B - 直接下载（无需 Homebrew）:"
        echo "    访问 https://github.com/cli/cli/releases"
        echo "    下载 gh_2.x.x_macOS_arm64.zip"
        echo "    解压后将 bin/gh 放入 /usr/local/bin/"
        echo ""
        echo "安装 gh 后，重新运行此脚本。"
        exit 1
    fi
}

# Step 2: 检查 GitHub 认证
check_auth() {
    if gh auth status &> /dev/null; then
        echo "✅ GitHub 已认证"
    else
        echo "❌ 未登录 GitHub"
        echo ""
        echo "运行以下命令登录："
        echo "  gh auth login"
        echo ""
        echo "推荐使用浏览器登录（最简单）："
        echo "  gh auth login --web"
        echo ""
        exit 1
    fi
}

# Step 3: 初始化 Git 仓库
init_git() {
    cd "$REPO_DIR"
    echo ""
    echo "📦 初始化 Git 仓库..."
    
    # 初始化 git（如果尚未初始化）
    if [ ! -d .git ]; then
        git init
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
        echo "✅ Git 仓库初始化完成"
    else
        echo "✅ Git 仓库已存在"
    fi
    
    # 创建 .gitignore
    if [ ! -f .gitignore ]; then
        cat > .gitignore << 'EOF'
__pycache__/
*.pyc
.DS_Store
*.wechat.html
*.local.html
.env
EOF
        echo "✅ .gitignore 已创建"
    fi
    
    # 提交所有文件
    echo ""
    echo "📝 提交文件..."
    git add .
    git commit -m "✨ 初始提交: wechat-formatter-luojiswei v2.3.1

- 罗辑思维风格微信公众号排版工具
- 支持 Markdown 转微信 HTML
- 支持一键发布微信草稿箱
- MIT License"
    echo "✅ 提交完成"
}

# Step 4: 创建 GitHub 仓库并推送
create_and_push() {
    echo ""
    echo "🚀 创建 GitHub 仓库并推送..."
    
    # 使用 gh api 创建仓库
    gh repo create "$REPO_NAME" \
        --public \
        --description "微信公众号排版工具 · 罗辑思维风格 — 让文章读起来更舒服，写起来更专注。" \
        --source="$REPO_DIR" \
        --remote=origin \
        --push \
        2>&1 || {
            echo ""
            echo "⚠️ 仓库可能已存在，尝试直接推送..."
            git branch -M main
            git push -u origin main --force 2>&1
        }
    
    echo ""
    echo "========================================"
    echo "  🎉 发布成功！"
    echo "========================================"
    echo ""
    echo "📎 仓库地址: https://github.com/$GITHUB_USER/$REPO_NAME"
    echo "📎 Clone:     git clone https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo ""
}

# 主流程
check_gh
check_auth
init_git
create_and_push
