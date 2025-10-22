"""
LLM Agent Module
Handles natural language understanding and Python code generation
"""
from typing import Dict, List, Optional, Any
import json
import logging
from openai import OpenAI
from anthropic import Anthropic
from backend.config import settings

logger = logging.getLogger(__name__)


def make_json_serializable(obj):
    """Convert objects to JSON-serializable format"""
    if isinstance(obj, dict):
        return {k: make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    elif hasattr(obj, '__dict__'):  # Custom objects
        return str(obj)
    else:
        return obj


class LLMAgent:
    """Agent for natural language understanding and code generation"""
    
    def __init__(self, provider: str = None, model: str = None):
        self.provider = provider or settings.llm_provider
        self.model = model or settings.model_name
        self._client = None  # Lazy initialization
    
    @property
    def client(self):
        """Lazy initialize the LLM client"""
        if self._client is None:
            if self.provider == "openai":
                if not settings.openai_api_key or settings.openai_api_key == "your_openai_api_key_here":
                    raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
                self._client = OpenAI(api_key=settings.openai_api_key)
            elif self.provider == "anthropic":
                if not settings.anthropic_api_key or settings.anthropic_api_key == "your_anthropic_api_key_here":
                    raise ValueError("Anthropic API key not configured. Please set ANTHROPIC_API_KEY in .env file")
                self._client = Anthropic(api_key=settings.anthropic_api_key)
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        return self._client
    
    def understand_query(self, query: str, available_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Understand user's natural language query and extract analysis intent
        
        Args:
            query: User's natural language question
            available_data: Information about available Excel data
            
        Returns:
            Dictionary containing:
            - intent: Type of analysis (sum, group, trend, sort, etc.)
            - target_columns: Columns to be used
            - operation: Specific operation to perform
            - filters: Any filtering conditions
        """
        system_prompt = """你是一个Excel数据分析助手。你的任务是理解用户的自然语言问题，并识别他们想要进行的数据分析类型。

分析以下可用的数据信息，并从用户的问题中提取：
1. 分析意图（如：求和、分组统计、趋势分析、排序、筛选等）
2. 需要使用的数据列
3. 具体的操作步骤
4. 任何筛选或过滤条件

请以JSON格式返回结果，包含以下字段：
- intent: 分析意图的简短描述
- analysis_type: 分析类型（sum/groupby/trend/sort/filter/correlation/visualization等）
- target_columns: 需要使用的列名列表
- operations: 具体操作步骤的列表
- filters: 筛选条件（如果有）
- expected_output: 期望的输出类型（table/chart/summary）
"""
        
        # Convert available_data to be JSON serializable
        json_safe_data = make_json_serializable(available_data)

        user_prompt = f"""可用数据信息：
{json.dumps(json_safe_data, ensure_ascii=False, indent=2)}

用户问题：{query}

请分析这个问题并返回JSON格式的分析计划。"""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                result = json.loads(response.choices[0].message.content)
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2048,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ],
                    temperature=0.3
                )
                result = json.loads(response.content[0].text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error understanding query: {e}")
            raise
    
    def generate_code(self, query: str, data_info: Dict[str, Any], 
                     analysis_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate Python code based on the analysis plan
        
        Args:
            query: Original user query
            data_info: Information about the data
            analysis_plan: Analysis plan from understand_query
            
        Returns:
            Dictionary containing:
            - code: Generated Python code
            - explanation: Code explanation
            - required_columns: List of columns used
            - output_type: Type of output (dataframe/plot/summary)
        """
        system_prompt = """你是一个Python代码生成专家。你的任务是根据分析计划生成高质量的Python数据分析代码。

代码要求：
1. 使用pandas进行数据处理
2. 使用matplotlib/seaborn/plotly进行可视化
3. 代码应该清晰、注释完整
4. 处理可能的异常情况
5. 返回结果应该易于理解

6. **图形对象管理** (重要): 整个绘图过程中只能创建一个图形对象：
   - 只在绘图开始时调用一次 plt.figure(figsize=(16, 8))
   - 后续绘图代码不应再调用 plt.figure()

7. **中文字体配置** (重要): 如果使用matplotlib/seaborn绘图，必须在绘图代码之前添加：
   ```python
   # 配置中文字体支持
   plt.rcParams['font.sans-serif'] = [
       'Noto Sans CJK SC', 'WenQuanYi Micro Hei', 'Droid Sans Fallback',
       'PingFang SC', 'Heiti SC', 'STHeiti',
       'SimHei', 'Microsoft YaHei',
       'Arial Unicode MS', 'sans-serif'
   ]
   plt.rcParams['axes.unicode_minus'] = False
   ```

8. **日期/时间序列图表的X轴标签处理** (非常重要):
   对于包含日期数据的趋势图，必须使用matplotlib的日期格式化器来避免标签重叠：
   
   ```python
   # 在绘图代码之后，添加以下X轴优化代码
   import matplotlib.dates as mdates
   
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
   
   注意：如果数据点非常多（>50），考虑先聚合数据（按周或按月），而不是显示每个数据点。

9. **非日期图表的X轴标签处理**:
   对于分类数据或其他类型的X轴标签，如果标签较多（>15个），使用：
   ```python
   plt.xticks(rotation=45, ha='right', fontsize=9)
   plt.tight_layout()
   ```

10. **图表尺寸**: 对于趋势图，推荐使用 figsize=(16, 8)；对于简单图表，使用 figsize=(12, 6)

生成的代码应该是完整可执行的，包含必要的import语句。
代码中应该假设数据已经加载到名为'df'的DataFrame中。

请返回JSON格式，包含：
- code: 完整的Python代码
- explanation: 代码的中文解释
- required_columns: 使用的列名列表
- output_type: 输出类型（dataframe/plot/summary/mixed）
- visualization_needed: 是否需要可视化（true/false）
"""
        
        # Convert data_info and analysis_plan to JSON-serializable format
        json_safe_data_info = make_json_serializable(data_info)
        json_safe_analysis_plan = make_json_serializable(analysis_plan)

        user_prompt = f"""数据信息：
{json.dumps(json_safe_data_info, ensure_ascii=False, indent=2)}

分析计划：
{json.dumps(json_safe_analysis_plan, ensure_ascii=False, indent=2)}

用户原始问题：{query}

请生成相应的Python代码。"""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                result = json.loads(response.choices[0].message.content)
            else:  # anthropic
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=4096,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ],
                    temperature=0.2
                )
                result = json.loads(response.content[0].text)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating code: {e}")
            raise
    
    def select_relevant_files(self, query: str, 
                            available_files: List[Dict[str, Any]]) -> List[str]:
        """
        Select the most relevant Excel files for the query
        
        Args:
            query: User's question
            available_files: List of available file information
            
        Returns:
            List of selected file paths
        """
        if not available_files:
            return []
        
        if len(available_files) == 1:
            return [available_files[0]['path']]
        
        system_prompt = """你是一个数据文件选择助手。根据用户的问题和可用文件的信息，选择最相关的文件。

请返回JSON格式：
- selected_files: 选中的文件路径列表
- reason: 选择理由
"""
        
        files_info = "\n".join([
            f"文件 {i+1}: {f['name']}\n列: {', '.join(f.get('columns', []))}\n预览: {f.get('preview', 'N/A')}"
            for i, f in enumerate(available_files)
        ])
        
        user_prompt = f"""可用文件：
{files_info}

用户问题：{query}

请选择最相关的文件。"""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3
                )
                result = json.loads(response.choices[0].message.content)
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ],
                    temperature=0.3
                )
                result = json.loads(response.content[0].text)
            
            return result.get('selected_files', [])
            
        except Exception as e:
            logger.error(f"Error selecting files: {e}")
            # Fallback: return all files
            return [f['path'] for f in available_files]
    
    def create_summary(self, query: str, code: str, result: Any, 
                      columns_used: List[str]) -> str:
        """
        Create a natural language summary of the analysis results
        
        Args:
            query: Original query
            code: Executed code
            result: Analysis result
            columns_used: Columns that were used
            
        Returns:
            Natural language summary
        """
        system_prompt = """你是一个数据分析结果总结助手。请用清晰、简洁的中文总结分析结果。

总结应包括：
1. 回答用户的问题
2. 关键发现和洞察
3. 使用的数据列
4. 任何需要注意的事项
"""
        
        # Convert result to string representation
        if hasattr(result, 'to_string'):
            result_str = result.to_string()
        elif hasattr(result, 'to_dict'):
            # Convert to dict first, then to JSON-serializable format
            result_dict = result.to_dict()
            json_safe_result = make_json_serializable(result_dict)
            result_str = json.dumps(json_safe_result, ensure_ascii=False, indent=2)
        else:
            result_str = str(result)
        
        # Limit result string length
        if len(result_str) > 2000:
            result_str = result_str[:2000] + "...(结果已截断)"
        
        user_prompt = f"""用户问题：{query}

执行的代码：
{code}

分析结果：
{result_str}

使用的数据列：{', '.join(columns_used)}

请提供分析结果的总结。"""
        
        try:
            if self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.5
                )
                summary = response.choices[0].message.content
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"}
                    ],
                    temperature=0.5
                )
                summary = response.content[0].text
            
            return summary
            
        except Exception as e:
            logger.error(f"Error creating summary: {e}")
            return f"分析完成。使用的数据列：{', '.join(columns_used)}"

