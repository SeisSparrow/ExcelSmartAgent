# Ubuntu 中文字体支持 - 更改总结

## 📋 问题描述

在 Ubuntu/Linux 系统上，matplotlib 生成的图表中中文标题和标签显示为方框（□□□）或乱码。

## ✅ 已完成的修复

### 1. 更新字体配置 (核心修复)

**文件**: `backend/core/llm_agent.py`

**修改内容**:
- 在 LLM 提示词中更新了字体配置列表
- 添加了 Linux 常用中文字体（优先级最高）：
  - Noto Sans CJK SC
  - WenQuanYi Micro Hei
  - Droid Sans Fallback
  - DejaVu Sans
- 保留了 macOS 和 Windows 字体的支持
- 添加了详细的注释说明

**代码示例**:
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
```

### 2. 更新 Dockerfile (Docker 支持)

**文件**: `Dockerfile`

**修改内容**:
- 添加了中文字体包安装
- 添加了 fontconfig 工具
- 添加了字体缓存刷新命令

**新增依赖**:
```dockerfile
RUN apt-get update && apt-get install -y \
    fonts-noto-cjk \
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    fontconfig \
    && fc-cache -fv \
    && rm -rf /var/lib/apt/lists/*
```

### 3. 更新可视化指南文档

**文件**: `VISUALIZATION_GUIDE.md`

**修改内容**:
- 更新了"中文字体支持"章节
- 添加了跨平台支持说明（macOS、Windows、Linux）
- 添加了 Ubuntu/Linux 用户的字体安装指令
- 添加了清除 matplotlib 缓存的说明

### 4. 更新故障排除文档

**文件**: `TROUBLESHOOTING.md`

**修改内容**:
- 添加了新的第 7 节："图表中文显示问题（Ubuntu/Linux）"
- 提供了 5 个详细步骤的修复流程
- 包含了针对不同 Linux 发行版的安装命令
- 添加了 Docker 环境的特殊配置说明
- 包含了字体验证和 Python 测试脚本
- 提供了故障诊断建议

### 5. 创建一键修复脚本

**文件**: `fix_chinese_fonts_ubuntu.sh` (新建)

**功能**:
- ✅ 自动检测 Linux 发行版（Ubuntu/Debian/CentOS/RHEL/Fedora）
- ✅ 安装适合的中文字体包
- ✅ 刷新系统字体缓存
- ✅ 清除 matplotlib 缓存
- ✅ 验证字体安装
- ✅ 提供详细的下一步操作指引

**使用方法**:
```bash
bash fix_chinese_fonts_ubuntu.sh
```

### 6. 创建中文字体测试脚本

**文件**: `test_chinese_font.py` (新建)

**功能**:
- ✅ 检测系统中可用的中文字体
- ✅ 显示 matplotlib 配置
- ✅ 显示实际使用的字体
- ✅ 生成包含中文的测试图表（4 种图表类型）
- ✅ 提供详细的诊断信息
- ✅ 给出修复建议

**生成的测试图表**:
1. 折线图 - 销售额趋势
2. 柱状图 - 城市销售额对比
3. 饼图 - 产品类别占比
4. 散点图 - 价格与销量关系

**使用方法**:
```bash
python test_chinese_font.py
# 查看生成的 test_chinese_display.png
```

### 7. 更新主文档

**文件**: `README.md`

**修改内容**:
- 在"常见问题"部分添加了"Ubuntu/Linux 图表中文显示问题"
- 提供了快速修复命令
- 包含了 Docker 用户的特别说明
- 添加了测试脚本的使用说明

### 8. 创建专门的修复指南

**文件**: `UBUNTU_CHINESE_FONT_FIX.md` (新建)

**内容**:
- 完整的问题描述
- 两种修复方法（一键脚本 + 手动安装）
- Docker 环境的特殊处理
- 测试和验证步骤
- 支持的字体列表
- 详细的故障排除指南
- 技术细节说明

## 🎯 支持的平台

修复后，系统现在完全支持：

| 平台 | 状态 | 推荐字体 |
|------|------|----------|
| Ubuntu/Debian | ✅ 完全支持 | Noto Sans CJK SC, WenQuanYi Micro Hei |
| CentOS/RHEL | ✅ 完全支持 | Google Noto Sans CJK, WenQuanYi Micro Hei |
| Fedora | ✅ 完全支持 | Google Noto Sans CJK, WenQuanYi Micro Hei |
| macOS | ✅ 完全支持 | PingFang SC, Heiti SC |
| Windows | ✅ 完全支持 | SimHei, Microsoft YaHei |
| Docker (Linux) | ✅ 完全支持 | Noto Sans CJK SC (已内置) |

## 📦 新增文件

1. `fix_chinese_fonts_ubuntu.sh` - 一键修复脚本（可执行）
2. `test_chinese_font.py` - 字体测试脚本（可执行）
3. `UBUNTU_CHINESE_FONT_FIX.md` - Ubuntu 专用修复指南
4. `CHANGES_SUMMARY.md` - 本文件（更改总结）

## 🔄 修改的文件

1. `backend/core/llm_agent.py` - 更新字体配置
2. `Dockerfile` - 添加字体包
3. `VISUALIZATION_GUIDE.md` - 更新文档
4. `TROUBLESHOOTING.md` - 添加故障排除
5. `README.md` - 添加常见问题

## 📝 使用说明

### 对于新用户

如果您是 Ubuntu/Linux 用户，首次使用时：

1. **运行一键修复脚本**:
   ```bash
   bash fix_chinese_fonts_ubuntu.sh
   ```

2. **测试中文显示**:
   ```bash
   python test_chinese_font.py
   ```

3. **重启服务**:
   ```bash
   # Docker 用户
   docker-compose restart
   
   # 直接运行用户
   python -m backend.main
   ```

### 对于现有用户

如果您之前已经部署了系统：

1. **拉取最新代码**:
   ```bash
   git pull
   ```

2. **如果使用 Docker，重建镜像**:
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up -d
   ```

3. **如果直接运行，安装字体**:
   ```bash
   bash fix_chinese_fonts_ubuntu.sh
   python -m backend.main
   ```

## 🧪 验证修复

运行测试查询，例如：
```
"画出销售额趋势图"
"显示各地区销售额对比柱状图"
"生成产品类别占比饼图"
```

检查生成的图表：
- ✅ 标题应该显示为中文（不是方框）
- ✅ 轴标签应该正确显示
- ✅ 图例和数据标签应该清晰可读

## 📚 相关文档

- **主要文档**: [README.md](README.md)
- **快速开始**: [QUICKSTART.md](QUICKSTART.md)
- **可视化指南**: [VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)
- **故障排除**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Ubuntu 修复**: [UBUNTU_CHINESE_FONT_FIX.md](UBUNTU_CHINESE_FONT_FIX.md)

## 🐛 已知问题

无已知问题。如有问题请提交 Issue。

## 💡 技术说明

### 为什么选择这些字体？

1. **Noto Sans CJK SC** - Google 开源，覆盖面广，质量高
2. **WenQuanYi Micro Hei** - 开源中文字体，Ubuntu 常用
3. **Droid Sans Fallback** - Android 字体，兼容性好

### 字体优先级

matplotlib 会按配置列表的顺序尝试使用字体，使用第一个可用的字体。因此：
- Linux 字体放在最前面（Linux 系统优先使用）
- 然后是 macOS 字体
- 最后是 Windows 字体
- 以 sans-serif 作为最终备选

### 缓存机制

matplotlib 会缓存字体列表以提高性能。因此：
- 安装新字体后必须清除缓存
- 缓存位置：`~/.cache/matplotlib/`
- Docker 容器重建时会自动清除缓存

## 🎉 影响

修复后的改进：
- ✅ 支持所有主流 Linux 发行版
- ✅ Docker 环境开箱即用
- ✅ 提供自动化修复工具
- ✅ 完善的文档和故障排除指南
- ✅ 可验证的测试工具

---

**更新日期**: 2025-10-22  
**版本**: v1.0  
**状态**: ✅ 完成并测试

