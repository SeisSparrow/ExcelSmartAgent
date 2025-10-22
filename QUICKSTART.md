# ⚡ 快速开始指南

5分钟快速上手 Excel Smart Agent。

## 📋 前置要求

- Python 3.11
- OpenAI 或 Anthropic API 密钥
- 现代浏览器

## 🚀 三步启动

### 第 1 步：安装

```bash
cd ExcelSmartAgent
./fix_and_run.sh
```

脚本会自动：
- 创建Python虚拟环境
- 安装所有依赖
- 创建配置文件

**耗时**: 约3-5分钟

### 第 2 步：配置API密钥

编辑 `.env` 文件：
```bash
nano .env
```

填入您的密钥：
```
OPENAI_API_KEY=sk-your-actual-key-here
```

**获取密钥:**
- OpenAI: https://platform.openai.com
- Anthropic: https://console.anthropic.com

### 第 3 步：启动

```bash
./start.sh
```

打开浏览器: http://localhost:8000

## 🎯 第一次使用

### 1. 生成测试数据

```bash
python examples/sample_data.py
```

会生成3个示例Excel文件：
- `sales_data_sample.xlsx` - 销售数据
- `inventory_sample.xlsx` - 库存数据
- `customer_sample.xlsx` - 客户数据

### 2. 上传文件

在Web界面：
1. 拖拽或点击上传 `sales_data_sample.xlsx`
2. 等待处理完成

### 3. 输入查询

尝试这些问题：

**简单查询：**
```
计算总销售额
```

**分析查询：**
```
分析各地区的销售趋势
```

**可视化查询：**
```
绘制各地区销售额的柱状图
```

### 4. 查看结果

系统会显示：
- ✅ 使用的数据列
- ✅ 生成的Python代码
- ✅ 执行结果
- ✅ 可视化图表
- ✅ 智能总结

## 💡 更多示例

查看 `examples/sample_query.md` 获取30+示例查询。

## 🔧 常见问题

### 安装失败？

**Python版本问题：**
```bash
python3.11 --version  # 确认是3.11版本
```

**SSL证书错误：**
```bash
pip config set global.trusted-host "pypi.tuna.tsinghua.edu.cn files.pythonhosted.org"
```

**重新安装：**
```bash
rm -rf venv/
./fix_and_run.sh
```

### 服务启动失败？

**端口被占用：**
编辑 `.env` → 改为 `PORT=8080`

**依赖问题：**
查看 `logs/app.log`

### 语音不工作？

语音是可选功能。文本查询完全可用。

如需启用：
```bash
brew install portaudio
pip install pyaudio speechrecognition
```

## 📚 下一步

- 📖 阅读完整文档: `README.md`
- 🐛 故障排除: `TROUBLESHOOTING.md`
- 💻 API文档: http://localhost:8000/docs
- 📁 示例查询: `examples/sample_query.md`

## 🆘 获取帮助

遇到问题？

1. 查看日志: `logs/app.log`
2. 检查配置: `.env` 文件
3. 参考文档: `TROUBLESHOOTING.md`
4. 提交Issue: GitHub Issues

---

**祝您使用愉快！** 🎉
