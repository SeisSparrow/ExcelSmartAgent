#!/usr/bin/env python3
"""
中文字体测试脚本
用于验证 matplotlib 中文显示是否正常
"""
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import sys
import os

print("=" * 60)
print("  matplotlib 中文字体测试")
print("=" * 60)
print()

# 1. 显示 matplotlib 版本
print(f"📦 matplotlib 版本: {matplotlib.__version__}")
print()

# 2. 配置中文字体（与项目中使用的配置一致）
print("🔧 配置中文字体...")
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

print("✅ 字体配置完成")
print()

# 3. 显示实际使用的字体
print("📝 当前配置的字体列表:")
for i, font in enumerate(plt.rcParams['font.sans-serif'][:5], 1):
    print(f"  {i}. {font}")
print()

# 4. 检查系统中可用的中文字体
print("🔍 系统中可用的中文字体:")
chinese_fonts = []
font_files = fm.findSystemFonts(fontpaths=None, fontext='ttf')
font_files += fm.findSystemFonts(fontpaths=None, fontext='ttc')

for font_file in font_files:
    font_lower = font_file.lower()
    if any(keyword in font_lower for keyword in ['noto', 'wenquanyi', 'wqy', 'simhei', 'simsun', 'pingfang', 'heiti', 'yahei', 'droid']):
        try:
            font_prop = fm.FontProperties(fname=font_file)
            font_name = font_prop.get_name()
            if font_name not in chinese_fonts:
                chinese_fonts.append(font_name)
                print(f"  ✓ {font_name}")
                if len(chinese_fonts) >= 10:  # 限制显示数量
                    break
        except:
            pass

if not chinese_fonts:
    print("  ⚠️  未找到中文字体！")
    print("  请运行: sudo apt-get install fonts-noto-cjk fonts-wqy-microhei")
    sys.exit(1)

print()

# 5. 获取实际使用的字体
print("🎯 matplotlib 实际使用的字体:")
try:
    # 创建一个临时图表来检测实际使用的字体
    fig, ax = plt.subplots(figsize=(1, 1))
    text = ax.text(0.5, 0.5, '测试', fontsize=12)
    fig.canvas.draw()
    actual_font = text.get_fontname()
    print(f"  ➜ {actual_font}")
    plt.close(fig)
except Exception as e:
    print(f"  ⚠️  无法检测实际字体: {e}")

print()

# 6. 创建测试图表
print("📊 生成测试图表...")

try:
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('中文字体显示测试 - Excel Smart Agent', fontsize=16, fontweight='bold')
    
    # 图表 1: 折线图
    x_data = ['一月', '二月', '三月', '四月', '五月', '六月']
    y_data = [120, 135, 158, 172, 195, 210]
    ax1.plot(x_data, y_data, marker='o', linewidth=2, markersize=8)
    ax1.set_title('销售额趋势图', fontsize=14)
    ax1.set_xlabel('月份', fontsize=12)
    ax1.set_ylabel('销售额（万元）', fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)
    
    # 图表 2: 柱状图
    categories = ['北京', '上海', '广州', '深圳', '杭州']
    values = [85, 92, 78, 88, 81]
    bars = ax2.bar(categories, values, color=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8'])
    ax2.set_title('各城市销售额对比', fontsize=14)
    ax2.set_xlabel('城市', fontsize=12)
    ax2.set_ylabel('销售额（万元）', fontsize=12)
    ax2.tick_params(axis='x', rotation=45)
    
    # 在柱状图上显示数值
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{height}万',
                ha='center', va='bottom', fontsize=10)
    
    # 图表 3: 饼图
    sizes = [30, 25, 20, 15, 10]
    labels = ['电子产品', '服装鞋帽', '食品饮料', '日用百货', '其他']
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    ax3.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
            startangle=90, textprops={'fontsize': 11})
    ax3.set_title('产品类别占比', fontsize=14)
    
    # 图表 4: 散点图
    import numpy as np
    np.random.seed(42)
    x = np.random.randn(50) * 10 + 50
    y = np.random.randn(50) * 10 + 50
    colors_scatter = np.random.rand(50)
    ax4.scatter(x, y, c=colors_scatter, s=100, alpha=0.6, cmap='viridis')
    ax4.set_title('价格与销量关系', fontsize=14)
    ax4.set_xlabel('价格（元）', fontsize=12)
    ax4.set_ylabel('销量（件）', fontsize=12)
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图表
    output_file = 'test_chinese_display.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight', facecolor='white')
    print(f"✅ 测试图表已保存: {output_file}")
    
    # 检查文件是否创建
    if os.path.exists(output_file):
        file_size = os.path.getsize(output_file) / 1024  # KB
        print(f"   文件大小: {file_size:.1f} KB")
    
    plt.close()
    
except Exception as e:
    print(f"❌ 生成图表失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 7. 验证结果
print("=" * 60)
print("  ✅ 测试完成！")
print("=" * 60)
print()
print("📋 请检查生成的图片:")
print(f"   {os.path.abspath(output_file)}")
print()
print("🔍 验证要点:")
print("   1. 图表标题是否显示为汉字（不是方框 □□□）")
print("   2. 轴标签是否正确显示中文")
print("   3. 图例和数据标签是否正常")
print("   4. 饼图的标签是否清晰可读")
print()

# 8. 额外提示
if not chinese_fonts:
    print("⚠️  警告: 未检测到中文字体")
    print()
    print("建议执行:")
    print("   Ubuntu/Debian: sudo apt-get install fonts-noto-cjk fonts-wqy-microhei")
    print("   CentOS/RHEL:   sudo yum install google-noto-sans-cjk-fonts")
    print("   然后清除缓存: rm -rf ~/.cache/matplotlib")
    print()
elif len(chinese_fonts) < 2:
    print("ℹ️  提示: 仅检测到较少的中文字体，建议安装更多字体以获得更好的显示效果")
    print()

print("💡 如果中文仍然显示为方框:")
print("   1. 运行字体修复脚本: bash fix_chinese_fonts_ubuntu.sh")
print("   2. 清除 matplotlib 缓存: rm -rf ~/.cache/matplotlib")
print("   3. 重启 Python 环境或系统")
print("   4. 查看故障排除文档: TROUBLESHOOTING.md")
print()
print("=" * 60)

