# 故障排除指南

## Python 版本问题

### 问题: pandas 安装失败 (Python 3.13)

**错误信息**:
```
error: too few arguments to function call, expected 6, have 5
_PyLong_AsByteArray
```

**原因**: Python 3.13 是最新版本，某些包可能还不完全支持。

**解决方案**:

#### 方法1: 使用 Python 3.11 或 3.12（推荐）✅

```bash
# Mac (使用 Homebrew)
brew install python@3.11

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 验证版本
python --version

# 重新安装依赖
pip install --upgrade pip
pip install -r requirements.txt
```

#### 方法2: 使用 conda

```bash
# 创建指定 Python 版本的环境
conda create -n excel-agent python=3.11
conda activate excel-agent

# 安装依赖
pip install -r requirements.txt
```

#### 方法3: 使用 pyenv

```bash
# 安装 pyenv
curl https://pyenv.run | bash

# 安装 Python 3.11
pyenv install 3.11.7

# 设置本地版本
pyenv local 3.11.7

# 创建虚拟环境
python -m venv venv
source venv/bin/activate
```

#### 方法4: 更新包版本（如果必须使用 3.13）

requirements.txt 已更新为兼容 Python 3.13 的版本：

```bash
# 清理旧的虚拟环境
rm -rf venv/

# 创建新环境
python3.13 -m venv venv
source venv/bin/activate

# 更新 pip
pip install --upgrade pip setuptools wheel

# 安装依赖
pip install -r requirements.txt
```

---

## 其他常见问题

### 1. pyaudio 安装失败

**Mac**:
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian**:
```bash
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio
```

**Windows**:
下载预编译包: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio

### 2. OpenSSL 错误

```bash
# Mac
brew install openssl
export LDFLAGS="-L/opt/homebrew/opt/openssl@3/lib"
export CPPFLAGS="-I/opt/homebrew/opt/openssl@3/include"
pip install -r requirements.txt
```

### 3. 端口被占用

```bash
# 查找占用端口的进程
lsof -ti:8000

# 杀死进程
kill -9 $(lsof -ti:8000)

# 或修改端口（编辑 .env）
PORT=8080
```

### 4. 麦克风权限错误

**错误**: "无法访问麦克风，请检查权限"

**快速解决**:

1. **使用正确的访问地址**（最常见原因）:
   ```
   ✅ http://localhost:8000
   ❌ http://0.0.0.0:8000 或 http://192.168.x.x:8000
   ```

2. **macOS 系统权限**:
   ```bash
   # 打开系统设置
   open "x-apple.systempreferences:com.apple.preference.security?Privacy_Microphone"
   ```
   - 找到您的浏览器（Chrome/Safari/Edge）
   - 勾选允许访问麦克风

3. **浏览器权限**:
   - Chrome: 地址栏左侧 🔒 → 网站设置 → 麦克风 → 允许
   - Safari: 设置 → 网站 → 麦克风 → localhost → 允许

4. **重置权限**:
   - 清除浏览器缓存和 Cookies
   - 刷新页面重新授权

**详细指南**: 查看 `MICROPHONE_SETUP.md`

### 5. API 连接失败

**检查清单**:
- [ ] API 密钥是否正确
- [ ] 网络连接是否正常
- [ ] 账户是否有余额
- [ ] 是否需要代理

**使用代理**:
```bash
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080
```

### 5. 模块导入错误

```bash
# 确保在虚拟环境中
which python  # 应该指向 venv/bin/python

# 重新安装依赖
pip install --force-reinstall -r requirements.txt

# 从项目根目录运行
python -m backend.main
```

### 6. 语音识别不工作

**浏览器权限**:
- Chrome: 设置 → 隐私和安全 → 网站设置 → 麦克风
- 确保允许 localhost 访问麦克风

**网络要求**:
- Google 语音识别需要联网
- 确保可以访问 Google 服务

### 7. 图表中文显示问题（Ubuntu/Linux）

**症状**: 图表中的中文标题和标签显示为方框（□□□）或乱码

**原因**: Ubuntu/Linux 系统缺少中文字体

**解决方案**:

#### 步骤 1: 安装中文字体

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei
```

**CentOS/RHEL/Fedora**:
```bash
sudo yum install google-noto-sans-cjk-fonts wqy-microhei-fonts
# 或
sudo dnf install google-noto-sans-cjk-fonts wqy-microhei-fonts
```

#### 步骤 2: 清除 matplotlib 缓存

```bash
# 清除字体缓存
rm -rf ~/.cache/matplotlib

# 如果使用 Docker，在容器内执行
docker-compose exec app rm -rf /root/.cache/matplotlib
```

#### 步骤 3: 重启服务

```bash
# 如果使用 Docker
docker-compose restart

# 如果直接运行
# 按 Ctrl+C 停止服务，然后重新启动
python -m backend.main
```

#### 步骤 4: 验证字体安装

```bash
# 检查可用的中文字体
fc-list :lang=zh | grep -E "(Noto|WenQuanYi)"

# 应该看到类似输出：
# /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc: Noto Sans CJK SC:style=Regular
# /usr/share/fonts/truetype/wqy/wqy-microhei.ttc: WenQuanYi Micro Hei:style=Regular
```

#### 步骤 5: Python 测试

创建测试脚本 `test_chinese_font.py`:
```python
import matplotlib.pyplot as plt
import matplotlib

# 配置中文字体
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'Droid Sans Fallback',
    'PingFang SC', 'SimHei', 'Microsoft YaHei', 'sans-serif'
]
plt.rcParams['axes.unicode_minus'] = False

# 检查字体
print("当前字体:", plt.rcParams['font.sans-serif'])
print("\n可用字体列表:")
for font in matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf'):
    if 'Noto' in font or 'WenQuanYi' in font or 'wqy' in font.lower():
        print(f"  ✓ {font}")

# 测试绘图
fig, ax = plt.subplots(figsize=(8, 6))
ax.plot([1, 2, 3], [1, 4, 2])
ax.set_title('测试中文标题', fontsize=16)
ax.set_xlabel('横轴标签')
ax.set_ylabel('纵轴标签')
plt.savefig('test_chinese.png', dpi=100, bbox_inches='tight')
print("\n✓ 测试图表已保存到 test_chinese.png")
print("请打开图片检查中文是否正常显示")
```

运行测试:
```bash
python test_chinese_font.py
```

#### Docker 环境配置

如果使用 Docker，需要在 `Dockerfile` 中添加字体安装：

```dockerfile
# 在 Dockerfile 中添加
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*
```

然后重新构建镜像：
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### 仍然无法显示？

如果以上步骤都完成后仍然无法显示中文，请尝试：

1. **手动指定字体文件**：
```python
import matplotlib.font_manager as fm

# 添加字体文件路径
font_path = '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'
fm.fontManager.addfont(font_path)
plt.rcParams['font.family'] = 'Noto Sans CJK SC'
```

2. **检查系统日志**：
```bash
tail -f logs/app.log | grep -i font
```

3. **联系支持**：提供以下信息
   - OS 版本: `lsb_release -a`
   - 已安装字体: `fc-list :lang=zh`
   - Python 版本: `python --version`
   - matplotlib 版本: `pip show matplotlib`

### 8. 文件上传失败

**检查**:
- 文件大小是否超过 50MB
- 文件格式是否支持（.xlsx, .xls, .csv）
- 磁盘空间是否充足

**调整限制**:
```bash
# 编辑 .env
MAX_FILE_SIZE=100MB
```

### 9. 内存不足

**增加内存限制**:
```bash
# 对于大文件，增加 Python 内存
export PYTHONMALLOC=malloc
ulimit -v unlimited  # Linux/Mac
```

**优化建议**:
- 分批处理大文件
- 使用 chunksize 参数读取
- 及时清理处理后的数据

### 10. WebSocket 连接断开

**可能原因**:
- 网络不稳定
- 服务器重启
- 超时设置

**解决**:
- 页面会自动重连
- 检查网络连接
- 查看日志: `logs/app.log`

### 11. Docker 相关问题

**容器无法启动**:
```bash
# 查看日志
docker-compose logs -f

# 重建容器
docker-compose down
docker-compose up --build

# 清理并重启
docker-compose down -v
docker system prune -a
docker-compose up -d
```

---

## 日志和调试

### 查看日志

```bash
# 应用日志
tail -f logs/app.log

# 实时日志（开发模式）
python -m uvicorn backend.main:app --reload --log-level debug
```

### 调试模式

编辑 `.env`:
```bash
DEBUG=True
```

### 测试安装

```bash
# 测试 Python 导入
python -c "import pandas, fastapi, openai; print('OK')"

# 测试服务启动
python -m backend.main

# 访问健康检查
curl http://localhost:8000/api/health
```

---

## 性能优化

### 慢速查询

1. **使用更快的模型**:
```bash
MODEL_NAME=gpt-3.5-turbo  # 更快
# 或
MODEL_NAME=claude-3-haiku-20240307
```

2. **限制数据量**:
```python
# 只使用前 1000 行
df = df.head(1000)
```

3. **缓存结果**:
- 相同查询会自动使用缓存（如果启用）

### 降低成本

1. 使用更便宜的模型
2. 优化 prompt 长度
3. 启用结果缓存
4. 批量处理查询

---

## 获取帮助

如果以上方法都无法解决问题：

1. **查看完整日志**: `logs/app.log`
2. **查看文档**: `README.md`, `QUICKSTART.md`
3. **提交 Issue**: 包含错误信息、Python 版本、操作系统
4. **讨论**: GitHub Discussions

### 提交 Issue 模板

```markdown
**环境信息**
- OS: macOS 14.0
- Python: 3.13.0
- pip list: [粘贴 pip list 输出]

**错误信息**
[粘贴完整错误信息]

**重现步骤**
1. ...
2. ...
3. ...

**期望行为**
[描述期望的结果]

**实际行为**
[描述实际发生的情况]

**日志**
[粘贴相关日志]
```

---

## 常用命令

```bash
# 完全重置环境
rm -rf venv/
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 更新所有包
pip install --upgrade -r requirements.txt

# 检查包版本
pip list | grep -E "(pandas|fastapi|openai)"

# 测试导入
python -c "from backend.core.excel_processor import ExcelProcessor; print('OK')"

# 生成测试数据
python examples/sample_data.py

# 运行测试
pytest tests/ -v

# 清理缓存
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

**最后更新**: 2025-10-22

如有其他问题，欢迎提 Issue！

