# 📊 Excel Smart Agent

基于AI的智能Excel数据分析系统，支持自然语言查询和实时语音输入。

## ✨ 核心功能

- 🤖 **智能分析**: 使用GPT-4/Claude理解自然语言，自动生成分析代码
- 📁 **Excel预处理**: 自动处理复杂表格，重塑为标准二维表
- 💬 **自然语言**: 支持中英文查询（如："分析各地区销售趋势"）
- 🎤 **语音输入**: 实时语音识别（需要安静环境和清晰发音）
- 🔍 **数据追溯**: 清晰显示使用的数据列
- 📈 **可视化**: 自动生成图表和统计分析（完美支持中文标签）
- ⚡ **实时通信**: WebSocket实时双向通信

## 🚀 快速开始

### 1. 安装

```bash
# 克隆项目
git clone https://github.com/yourusername/ExcelSmartAgent.git
cd ExcelSmartAgent

# 一键安装
./fix_and_run.sh
```

### 2. 配置API密钥

编辑 `.env` 文件：
```bash
OPENAI_API_KEY=sk-your-key-here
```

获取密钥：
- OpenAI: https://platform.openai.com
- Anthropic: https://console.anthropic.com

### 3. 启动服务

```bash
./start.sh
```

访问: http://localhost:8000

## 📖 使用示例

### 上传Excel文件
拖拽文件或点击上传区域，支持 `.xlsx`, `.xls`, `.csv`

### 输入查询

**文本查询：**
```
- "计算总销售额"
- "分析各地区的销售趋势"
- "找出销售额最高的10个产品"
- "显示月度销售统计"
```

**语音查询：**
1. 确保使用 `http://localhost:8000` 访问（不要用IP地址）
2. 点击 🎤 语音输入按钮
3. 首次使用需授予浏览器和系统麦克风权限
4. 清晰说出您的问题（等待1-2秒）
5. 点击 ⏹️ 停止录音

💡 如遇到"无法访问麦克风"错误，请查看 `MICROPHONE_SETUP.md`

提示：文本输入可使用 Ctrl+Enter 快速提交

### 查看结果

系统会显示：
- 📋 使用的数据列
- 💻 生成的Python代码
- 📊 分析结果（表格/图表）
- 📝 智能总结

## 🛠️ 技术栈

**后端:** FastAPI + pandas + OpenAI/Anthropic + WebSocket  
**前端:** JavaScript + WebSocket API + Web Audio API  
**数据处理:** pandas + openpyxl + matplotlib

## 📁 项目结构

```
ExcelSmartAgent/
├── backend/           # 后端服务
│   ├── core/         # 核心模块
│   ├── api/          # API接口
│   └── utils/        # 工具模块
├── frontend/         # Web界面
├── examples/         # 示例和测试数据
├── tests/           # 单元测试
└── data/            # 数据目录
```

## 🔧 常见问题

### SSL证书错误？
```bash
pip config set global.trusted-host "pypi.tuna.tsinghua.edu.cn files.pythonhosted.org"
```

### 端口被占用？
编辑 `.env` 文件，修改 `PORT=8080`

### 语音识别失败？

**语音输入技巧：**
- 🎤 在安静的环境中使用
- 📢 说话清晰、速度适中
- ⏱️ 说完后等待1-2秒再停止
- 🌐 确保网络连接正常（使用Google API）

**备选方案：**
如果语音识别不准确，建议使用文本输入（更快更准确）

详细故障排除：查看 `TROUBLESHOOTING.md`

## 🧪 测试

生成示例数据：
```bash
python examples/sample_data.py
```

运行测试：
```bash
pytest tests/ -v
```

## 📚 文档

- 📖 [快速开始指南](QUICKSTART.md) - 5分钟上手
- 📊 [数据可视化指南](VISUALIZATION_GUIDE.md) - 图表优化和最佳实践
- 🔧 [故障排除](TROUBLESHOOTING.md) - 常见问题解决
- 💡 [示例查询](examples/sample_query.md) - 查询示例

## 📚 API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- API信息: http://localhost:8000/api

## 🎯 支持的分析类型

- ✅ 聚合统计（求和、平均、计数等）
- ✅ 分组分析（Group By）
- ✅ 趋势分析和时间序列
- ✅ 数据排序和筛选
- ✅ 相关性分析
- ✅ 数据透视表
- ✅ 可视化图表（柱状图、折线图、饼图等）

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 开源协议

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/)
- [pandas](https://pandas.pydata.org/)
- [OpenAI](https://openai.com/)
- [Anthropic](https://www.anthropic.com/)

---

⭐ 如果这个项目对您有帮助，请给它一个星标！
