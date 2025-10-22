# Ubuntu 中文字体显示修复指南

## 问题描述

在 Ubuntu/Linux 系统上，matplotlib 生成的图表中中文显示为方框（□□□）或乱码。

## 快速修复（推荐）

### 方法 1: 使用一键修复脚本

```bash
# 在项目根目录执行
bash fix_chinese_fonts_ubuntu.sh
```

这个脚本会自动：
1. ✅ 检测系统类型（Ubuntu/Debian/CentOS/Fedora）
2. ✅ 安装合适的中文字体包
3. ✅ 刷新系统字体缓存
4. ✅ 清除 matplotlib 缓存
5. ✅ 验证字体安装

### 方法 2: 手动安装

**Ubuntu/Debian:**
```bash
# 1. 安装字体
sudo apt-get update
sudo apt-get install fonts-noto-cjk fonts-wqy-microhei fonts-wqy-zenhei

# 2. 清除缓存
rm -rf ~/.cache/matplotlib

# 3. 重启服务
python -m backend.main
```

**CentOS/RHEL:**
```bash
# 1. 安装字体
sudo yum install google-noto-sans-cjk-fonts wqy-microhei-fonts

# 2. 清除缓存
rm -rf ~/.cache/matplotlib

# 3. 重启服务
python -m backend.main
```

**Fedora:**
```bash
# 1. 安装字体
sudo dnf install google-noto-sans-cjk-fonts wqy-microhei-fonts

# 2. 清除缓存
rm -rf ~/.cache/matplotlib

# 3. 重启服务
python -m backend.main
```

## Docker 环境修复

Dockerfile 已经更新以支持中文字体。如果您使用 Docker：

```bash
# 重新构建镜像
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

新的 Dockerfile 包含：
```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*
```

## 测试中文显示

运行测试脚本验证修复效果：

```bash
python test_chinese_font.py
```

这会：
1. 检测系统中可用的中文字体
2. 显示 matplotlib 实际使用的字体
3. 生成包含中文的测试图表（`test_chinese_display.png`）
4. 提供详细的诊断信息

## 支持的字体

系统现在支持以下中文字体（按优先级）：

### Linux 字体
- **Noto Sans CJK SC** - Google 开源字体，推荐
- **WenQuanYi Micro Hei** - 文泉驿微米黑
- **WenQuanYi Zen Hei** - 文泉驿正黑
- **Droid Sans Fallback** - Android 字体

### macOS 字体
- PingFang SC - 苹方
- Heiti SC - 黑体
- STHeiti - 华文黑体

### Windows 字体
- SimHei - 中文黑体
- Microsoft YaHei - 微软雅黑

### 通用备选
- Arial Unicode MS
- sans-serif

## 验证安装

### 检查已安装的字体

```bash
# 列出所有中文字体
fc-list :lang=zh

# 只显示 Noto 和文泉驿字体
fc-list :lang=zh | grep -E "(Noto|WenQuanYi)"
```

### 验证 matplotlib 配置

```python
import matplotlib.pyplot as plt
print(plt.rcParams['font.sans-serif'])
# 应该看到包含中文字体的列表
```

## 故障排除

### 问题 1: 安装后仍然显示方框

**解决方案:**
```bash
# 1. 确认字体已安装
fc-list :lang=zh | grep -E "(Noto|WenQuanYi)"

# 2. 清除所有缓存
rm -rf ~/.cache/matplotlib
rm -rf ~/.matplotlib

# 3. 重启 Python 环境
# 如果使用虚拟环境，先停用再激活
deactivate
source venv/bin/activate

# 4. 重启服务
python -m backend.main
```

### 问题 2: Docker 容器中仍然无法显示

**解决方案:**
```bash
# 1. 完全重建镜像（不使用缓存）
docker-compose down
docker-compose build --no-cache

# 2. 清除 Docker 缓存
docker system prune -a

# 3. 重新启动
docker-compose up -d

# 4. 进入容器验证
docker-compose exec app bash
fc-list :lang=zh
```

### 问题 3: 权限错误

**解决方案:**
```bash
# 确保修复脚本有执行权限
chmod +x fix_chinese_fonts_ubuntu.sh

# 使用 sudo 安装字体
sudo bash fix_chinese_fonts_ubuntu.sh
```

### 问题 4: 某些中文字符仍然显示为方框

**可能原因:** 字体不完整或不支持某些字符

**解决方案:**
```bash
# 安装更完整的字体集
sudo apt-get install fonts-noto-cjk-extra fonts-arphic-ukai fonts-arphic-uming

# 清除缓存
rm -rf ~/.cache/matplotlib

# 重启服务
```

## 技术细节

### 字体配置原理

项目中的代码（`backend/core/llm_agent.py`）会自动配置字体：

```python
plt.rcParams['font.sans-serif'] = [
    # Linux常用字体
    'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'Droid Sans Fallback', 'DejaVu Sans',
    # macOS字体
    'PingFang SC', 'Heiti SC', 'STHeiti',
    # Windows字体
    'SimHei', 'Microsoft YaHei',
    # 通用备选
    'Arial Unicode MS', 'sans-serif'
]
plt.rcParams['axes.unicode_minus'] = False
```

matplotlib 会按顺序尝试使用这些字体，使用第一个可用的字体。

### 为什么需要清除缓存

matplotlib 会缓存字体列表以提高性能。安装新字体后，必须清除缓存才能让 matplotlib 识别新字体。

缓存位置：
- `~/.cache/matplotlib/` - 主缓存目录
- `~/.matplotlib/` - 旧版本缓存目录

## 相关文档

- **完整故障排除**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **可视化指南**: [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)

## 获取帮助

如果以上方法都无法解决问题，请：

1. 运行诊断脚本收集信息：
```bash
python test_chinese_font.py > font_diagnosis.txt 2>&1
fc-list :lang=zh >> font_diagnosis.txt
lsb_release -a >> font_diagnosis.txt
```

2. 提交 Issue，包含：
   - `font_diagnosis.txt` 的内容
   - 生成的测试图片 `test_chinese_display.png`
   - 操作系统版本
   - 是否使用 Docker

---

**最后更新**: 2025-10-22

如有其他问题，欢迎提 Issue！

