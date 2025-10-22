#!/bin/bash

###############################################################################
# Ubuntu 中文字体修复脚本
# 用于解决 matplotlib 图表中文显示问题
###############################################################################

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  Ubuntu 中文字体修复脚本"
echo "=========================================="
echo ""

# 检测操作系统
if [[ ! -f /etc/os-release ]]; then
    echo "❌ 无法检测操作系统类型"
    exit 1
fi

. /etc/os-release

echo "检测到系统: $NAME $VERSION"
echo ""

# 步骤 1: 安装中文字体
echo "📦 步骤 1/4: 安装中文字体..."
echo ""

if [[ "$ID" == "ubuntu" ]] || [[ "$ID" == "debian" ]]; then
    echo "正在安装字体包 (Ubuntu/Debian)..."
    sudo apt-get update
    sudo apt-get install -y fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei fontconfig
    
elif [[ "$ID" == "centos" ]] || [[ "$ID" == "rhel" ]]; then
    echo "正在安装字体包 (CentOS/RHEL)..."
    sudo yum install -y google-noto-sans-cjk-fonts wqy-microhei-fonts fontconfig
    
elif [[ "$ID" == "fedora" ]]; then
    echo "正在安装字体包 (Fedora)..."
    sudo dnf install -y google-noto-sans-cjk-fonts wqy-microhei-fonts fontconfig
    
else
    echo "⚠️  未识别的系统: $ID"
    echo "请手动安装以下字体包之一："
    echo "  - Noto Sans CJK SC"
    echo "  - WenQuanYi Micro Hei"
    echo "  - WenQuanYi Zen Hei"
    exit 1
fi

echo "✅ 字体包安装完成"
echo ""

# 步骤 2: 刷新字体缓存
echo "🔄 步骤 2/4: 刷新系统字体缓存..."
sudo fc-cache -fv > /dev/null 2>&1
echo "✅ 系统字体缓存已刷新"
echo ""

# 步骤 3: 清除 matplotlib 缓存
echo "🧹 步骤 3/4: 清除 matplotlib 缓存..."

# 清除当前用户的缓存
if [ -d "$HOME/.cache/matplotlib" ]; then
    rm -rf "$HOME/.cache/matplotlib"
    echo "✅ 已清除用户 matplotlib 缓存: $HOME/.cache/matplotlib"
else
    echo "ℹ️  未发现用户 matplotlib 缓存"
fi

# 如果以 sudo 运行，也清除 root 缓存
if [ -n "$SUDO_USER" ] && [ -d "/root/.cache/matplotlib" ]; then
    sudo rm -rf /root/.cache/matplotlib
    echo "✅ 已清除 root matplotlib 缓存"
fi

echo ""

# 步骤 4: 验证字体安装
echo "✅ 步骤 4/4: 验证字体安装..."
echo ""
echo "可用的中文字体："

if command -v fc-list &> /dev/null; then
    FONTS=$(fc-list :lang=zh | grep -E "(Noto|WenQuanYi|wqy)" | head -5)
    if [ -n "$FONTS" ]; then
        echo "$FONTS" | while IFS= read -r line; do
            FONT_NAME=$(echo "$line" | cut -d':' -f2 | cut -d'=' -f1)
            echo "  ✓ $FONT_NAME"
        done
    else
        echo "  ⚠️  警告: 未找到中文字体，可能需要重启系统"
    fi
else
    echo "  ⚠️  fc-list 命令不可用，无法验证"
fi

echo ""
echo "=========================================="
echo "  ✅ 修复完成！"
echo "=========================================="
echo ""
echo "📋 后续步骤："
echo ""
echo "1. 如果使用 Docker："
echo "   docker-compose down"
echo "   docker-compose build --no-cache"
echo "   docker-compose up -d"
echo ""
echo "2. 如果直接运行 Python："
echo "   # 重启服务（Ctrl+C 然后重新运行）"
echo "   python -m backend.main"
echo ""
echo "3. 测试中文显示："
echo "   python test_chinese_font.py"
echo ""
echo "4. 如果问题仍然存在："
echo "   - 尝试重启系统"
echo "   - 查看故障排除文档: TROUBLESHOOTING.md"
echo ""
echo "=========================================="

