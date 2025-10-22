#!/bin/bash

# ============================================================================
# Excel Smart Agent 启动脚本
# ============================================================================

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "============================================================================"
echo -e "${BLUE}🚀 Excel Smart Agent 启动中...${NC}"
echo "============================================================================"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ 虚拟环境不存在！${NC}"
    echo ""
    echo "请先运行安装脚本:"
    echo "  ./install.sh"
    exit 1
fi

# 激活虚拟环境
echo -e "${BLUE}▶ 激活虚拟环境...${NC}"
source venv/bin/activate

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  警告: .env 配置文件不存在${NC}"
    echo "创建默认配置文件..."
    cp .env.example .env 2>/dev/null || echo "OPENAI_API_KEY=your_key_here" > .env
    echo -e "${YELLOW}请编辑 .env 文件并填入 API 密钥${NC}"
    echo ""
fi

# 检查 API 密钥
if grep -q "your_.*_key_here" .env 2>/dev/null; then
    echo -e "${YELLOW}⚠️  警告: 检测到默认 API 密钥，请更新 .env 文件${NC}"
    echo ""
fi

# 启动服务器
echo -e "${GREEN}✓ 启动服务器...${NC}"
echo ""
echo "访问地址: ${BLUE}http://localhost:8000${NC}"
echo "API 文档: ${BLUE}http://localhost:8000/docs${NC}"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""
echo "============================================================================"
echo ""

# 启动 uvicorn
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

