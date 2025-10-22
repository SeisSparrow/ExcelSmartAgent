"""
正确的可视化代码示例 - 用于"帮我分析各地区的销售趋势"这类问题

这个示例展示了如何正确处理日期时间序列图表的X轴标签，避免畸形。
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# 假设数据已加载到df中
# 这里我们手动加载以便测试
df = pd.read_csv('../data/processed/sales_data_sample_Sheet1.csv')

# 确保日期列是datetime类型
df['日期'] = pd.to_datetime(df['日期'])

print("数据概览:")
print(f"- 数据行数: {len(df)}")
print(f"- 日期范围: {df['日期'].min()} 到 {df['日期'].max()}")
print(f"- 地区: {', '.join(df['地区'].unique())}")

# ============= 正确的可视化代码模板 =============

# 1. 配置中文字体支持
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'Droid Sans Fallback',
    'PingFang SC', 'Heiti SC', 'STHeiti',
    'SimHei', 'Microsoft YaHei',
    'Arial Unicode MS', 'sans-serif'
]
plt.rcParams['axes.unicode_minus'] = False

# 2. 创建图形对象（只调用一次）
plt.figure(figsize=(16, 8))

# 3. 绘制数据
for region in df['地区'].unique():
    region_data = df[df['地区'] == region]
    # 按日期分组计算每日销售额
    daily_sales = region_data.groupby('日期')['销售额'].sum().sort_index()
    # 绘制线图
    plt.plot(daily_sales.index, daily_sales.values, 
             marker='o', markersize=3, linewidth=2, label=region)

# 4. 设置图表标签和标题
plt.xlabel('日期', fontsize=12)
plt.ylabel('销售额', fontsize=12)
plt.title('各地区销售趋势分析', fontsize=14, fontweight='bold')
plt.legend(title='地区', fontsize=10, loc='best')
plt.grid(True, alpha=0.3)

# 5. 【关键】优化X轴日期标签 - 避免畸形
ax = plt.gca()

# 使用日期格式化器，自动选择合适的日期间隔
ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=15))  # 最多显示15个标签
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# 旋转标签避免重叠
plt.xticks(rotation=45, ha='right', fontsize=9)

# 自动格式化日期显示
plt.gcf().autofmt_xdate()

# 6. 最后调整布局
plt.tight_layout()

# 7. 保存图表
output_file = 'correct_region_sales_trend.png'
plt.savefig(output_file, dpi=100, bbox_inches='tight')
print(f"\n图表已保存到: {output_file}")

plt.close()

# ============= 额外优化：数据聚合版本（推荐用于大量数据点） =============
print("\n生成聚合版本（按周汇总）...")

plt.figure(figsize=(16, 8))

# 配置字体
plt.rcParams['font.sans-serif'] = [
    'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'Droid Sans Fallback',
    'PingFang SC', 'Heiti SC', 'STHeiti',
    'SimHei', 'Microsoft YaHei',
    'Arial Unicode MS', 'sans-serif'
]
plt.rcParams['axes.unicode_minus'] = False

# 添加周列
df_weekly = df.copy()
df_weekly['周'] = df_weekly['日期'].dt.to_period('W').dt.start_time

# 绘制按周聚合的数据
for region in df['地区'].unique():
    region_data = df_weekly[df_weekly['地区'] == region]
    weekly_sales = region_data.groupby('周')['销售额'].sum().sort_index()
    plt.plot(weekly_sales.index, weekly_sales.values, 
             marker='o', markersize=5, linewidth=2.5, label=region)

plt.xlabel('周（起始日期）', fontsize=12)
plt.ylabel('销售额', fontsize=12)
plt.title('各地区销售趋势分析（按周聚合）', fontsize=14, fontweight='bold')
plt.legend(title='地区', fontsize=10, loc='best')
plt.grid(True, alpha=0.3)

# 优化X轴
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=12))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
plt.xticks(rotation=45, ha='right', fontsize=9)
plt.gcf().autofmt_xdate()

plt.tight_layout()

output_file_weekly = 'correct_region_sales_trend_weekly.png'
plt.savefig(output_file_weekly, dpi=100, bbox_inches='tight')
print(f"周聚合图表已保存到: {output_file_weekly}")

plt.close()

print("\n✓ 完成！两个正确的图表已生成。")
print("\n关键要点:")
print("1. 使用 matplotlib.dates.AutoDateLocator 自动选择合适的日期间隔")
print("2. 使用 matplotlib.dates.DateFormatter 格式化日期标签")
print("3. 旋转X轴标签 (rotation=45, ha='right')")
print("4. 使用 plt.gcf().autofmt_xdate() 自动格式化")
print("5. 最后使用 plt.tight_layout() 调整布局")
print("6. 对于大量数据点，考虑先聚合（按周/月）再绘图")

