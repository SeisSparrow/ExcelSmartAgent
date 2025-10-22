# 可视化图表畸形问题修复指南

## 问题描述

当使用"帮我分析各地区的销售趋势"等涉及大量日期数据的查询时，生成的图表会出现以下问题：

1. **X轴标签密集重叠**：所有日期标签挤在一起，无法阅读
2. **数据点位置异常**：数据点可能挤在图表右侧
3. **图表布局混乱**：整体显示畸形

### 问题根源

当数据包含大量日期点（如1000行数据，每行一个日期）时，如果不做特殊处理，matplotlib会尝试显示所有日期标签，导致严重重叠。

## 解决方案

### 1. 核心修复：使用matplotlib的日期格式化器

对于所有包含日期/时间的趋势图，必须使用以下代码模式：

```python
import matplotlib.dates as mdates

# 在绘图代码之后添加：

# 获取当前坐标轴
ax = plt.gca()

# 使用日期格式化器，自动选择合适的日期间隔
ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=15))  # 最多显示15个标签
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

# 旋转标签避免重叠
plt.xticks(rotation=45, ha='right', fontsize=9)

# 自动格式化日期显示
plt.gcf().autofmt_xdate()

# 最后调整布局
plt.tight_layout()
```

### 2. 完整示例代码

请参考 `examples/correct_visualization_example.py`，其中包含：

- **方案1**：正确的日期时间序列图（使用日期格式化器）
- **方案2**：数据聚合版本（按周汇总，适用于大量数据点）

### 3. 关键点说明

#### AutoDateLocator

```python
ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=15))
```

- `AutoDateLocator` 会根据日期范围自动选择合适的间隔（天、周、月等）
- `maxticks=15` 限制最多显示15个标签，避免过度拥挤
- 可以根据图表大小调整此参数（10-20都是合理范围）

#### DateFormatter

```python
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
```

- 统一格式化日期标签
- 可以根据需要调整格式：
  - `'%Y-%m-%d'`：2024-10-21
  - `'%m/%d'`：10/21
  - `'%Y-%m'`：2024-10

#### autofmt_xdate()

```python
plt.gcf().autofmt_xdate()
```

- 自动格式化日期轴，包括旋转标签和调整间距
- 建议与 `plt.xticks(rotation=45, ha='right')` 一起使用以获得最佳效果

### 4. 数据聚合策略（推荐）

当数据点超过50个时，考虑先聚合数据：

#### 按周聚合

```python
df['周'] = df['日期'].dt.to_period('W').dt.start_time
weekly_data = df.groupby(['周', '地区'])['销售额'].sum().reset_index()
```

#### 按月聚合

```python
df['月'] = df['日期'].dt.to_period('M').dt.start_time
monthly_data = df.groupby(['月', '地区'])['销售额'].sum().reset_index()
```

聚合后的数据点更少，图表更清晰，趋势更明显。

### 5. 图表尺寸建议

- **趋势图**：`figsize=(16, 8)` - 更宽的图表能容纳更多标签
- **简单图表**：`figsize=(12, 6)` - 标准尺寸
- **多子图**：根据子图数量适当增加高度

### 6. 非日期图表的标签处理

对于分类数据或其他类型的X轴标签，如果标签较多：

```python
# 旋转标签
plt.xticks(rotation=45, ha='right', fontsize=9)

# 如果标签仍然重叠，可以减少字体大小
plt.xticks(rotation=45, ha='right', fontsize=7)

# 或者使用垂直旋转
plt.xticks(rotation=90, fontsize=8)

# 最后调整布局
plt.tight_layout()
```

## 已实施的修复

### llm_agent.py 更新

已更新 `backend/core/llm_agent.py` 中的 `generate_code()` 方法的系统提示词：

1. **简化了指导内容**：删除过于复杂的条件判断代码
2. **明确了日期图表处理**：提供清晰的代码模板
3. **强调了关键步骤**：使用 `AutoDateLocator` 和 `DateFormatter`
4. **增加了数据聚合建议**：当数据点>50时考虑聚合

### 测试验证

运行以下命令测试修复效果：

```bash
cd /Users/zhennan/Documents/GithubRepos/ExcelSmartAgent
./venv/bin/python examples/correct_visualization_example.py
```

生成的图表应该：
- ✓ X轴标签清晰可读，无重叠
- ✓ 标签均匀分布
- ✓ 数据点分布正常
- ✓ 整体布局美观

## 常见问题

### Q: 为什么标签仍然有轻微重叠？

A: 尝试：
1. 减少 `maxticks` 参数（如从15改为10）
2. 增加图表宽度（如 `figsize=(18, 8)`）
3. 减小字体大小（如 `fontsize=8` 或 `fontsize=7`）
4. 使用数据聚合

### Q: 日期格式不符合需求怎么办？

A: 修改 `DateFormatter` 的格式字符串：
- 只显示月-日：`'%m-%d'`
- 显示完整时间：`'%Y-%m-%d %H:%M'`
- 中文格式：`'%Y年%m月%d日'`（需要字体支持）

### Q: 数据点太多，图表仍然拥挤？

A: 
1. 优先使用数据聚合（按周或月）
2. 增加图表宽度到 `figsize=(20, 8)` 或更大
3. 考虑使用交互式图表（plotly）
4. 分拆为多个图表（如每个地区一个子图）

## 总结

修复图表畸形的关键是：

1. ✓ 使用 `matplotlib.dates.AutoDateLocator` 智能选择日期间隔
2. ✓ 使用 `matplotlib.dates.DateFormatter` 统一格式化
3. ✓ 旋转X轴标签（45度）
4. ✓ 使用 `plt.gcf().autofmt_xdate()` 自动优化
5. ✓ 对大量数据点先聚合再绘图
6. ✓ 使用合适的图表尺寸（趋势图推荐16x8）

遵循这些原则，可以确保生成的所有日期时间序列图表都清晰美观。

