#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "🔧 完全重置环境..."
rm -rf venv/

echo "📦 创建新环境（Python 3.11）..."
python3.11 -m venv venv
source venv/bin/activate

echo "⬆️  升级 pip..."
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org

echo "🌐 配置镜像源..."
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip config set global.trusted-host "pypi.tuna.tsinghua.edu.cn files.pythonhosted.org"

echo "📥 安装依赖（这可能需要几分钟）..."
pip install --trusted-host pypi.tuna.tsinghua.edu.cn --trusted-host files.pythonhosted.org \
    fastapi==0.109.0 \
    'uvicorn[standard]==0.27.0' \
    websockets==12.0 \
    python-multipart==0.0.6 \
    pandas==2.1.4 \
    numpy==1.26.3 \
    openpyxl==3.1.2 \
    xlrd==2.0.1 \
    openai==1.10.0 \
    httpx==0.24.1 \
    httpcore==0.17.3 \
    anthropic==0.18.0 \
    python-dotenv==1.0.0 \
    matplotlib==3.8.2 \
    seaborn==0.13.1 \
    plotly==5.18.0 \
    pydantic==2.5.3 \
    pydantic-settings==2.1.0 \
    aiofiles==23.2.1

echo "✅ 测试安装..."
python -c "import fastapi, pandas, openai; print('✅ 所有模块正常！')"

echo "📝 检查配置..."
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
OPENAI_API_KEY=your_openai_api_key_here
LLM_PROVIDER=openai
MODEL_NAME=gpt-4-turbo-preview
HOST=0.0.0.0
PORT=8000
DEBUG=True
EOF
    echo "⚠️  已创建 .env 文件，请编辑并填入 API 密钥"
fi

echo ""
echo "============================================"
echo "✅ 环境准备完成！"
echo "============================================"
echo ""
echo "下一步："
echo "1. 编辑 .env 文件填入 API 密钥: nano .env"
echo "2. 运行服务器: ./start.sh"
echo ""
echo "或者直接启动（按 Ctrl+C 停止）："
read -p "按 Enter 启动服务器，或 Ctrl+C 退出..."
echo ""
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

