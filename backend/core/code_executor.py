"""
Code Executor Module
Handles safe execution of generated Python code and data traceability
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional, Tuple
import io
import base64
import sys
from pathlib import Path
import logging
import traceback
import re

logger = logging.getLogger(__name__)


class CodeExecutor:
    """Execute generated Python code safely and track data usage"""
    
    def __init__(self):
        self.execution_history = []
        self.columns_accessed = set()
        
    def execute_code(self, code: str, data: pd.DataFrame, 
                    context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute Python code with given data
        
        Args:
            code: Python code to execute
            data: DataFrame containing the data
            context: Additional context variables
            
        Returns:
            Dictionary containing:
            - success: Whether execution succeeded
            - result: Execution result
            - output: Captured stdout
            - error: Error message if failed
            - columns_used: List of columns accessed
            - visualizations: List of generated plots (base64 encoded)
        """
        # Track columns accessed
        self.columns_accessed = set()
        
        # Prepare execution context
        exec_context = {
            'df': data,
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'px': px,
            'go': go,
            '__builtins__': __builtins__,
        }
        
        if context:
            exec_context.update(context)
        
        # Add column access tracking
        exec_context['df'] = self._create_tracked_dataframe(data)
        
        # Capture output
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        
        # Store plots
        visualizations = []
        
        try:
            # Execute code
            exec(code, exec_context)
            
            # Capture any matplotlib plots
            if plt.get_fignums():
                for fig_num in plt.get_fignums():
                    fig = plt.figure(fig_num)
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
                    buf.seek(0)
                    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                    visualizations.append({
                        'type': 'matplotlib',
                        'data': img_base64
                    })
                    plt.close(fig)
            
            # Get the result (last expression or assigned 'result' variable)
            result = exec_context.get('result', None)
            
            # If no explicit result, try to find the last meaningful variable
            if result is None:
                for var_name in ['output', 'final_result', 'ans', 'answer']:
                    if var_name in exec_context:
                        result = exec_context[var_name]
                        break
            
            output = captured_output.getvalue()
            
            # Extract columns used
            columns_used = list(self.columns_accessed)
            
            # Record execution
            self.execution_history.append({
                'code': code,
                'success': True,
                'columns_used': columns_used
            })
            
            return {
                'success': True,
                'result': result,
                'output': output,
                'error': None,
                'columns_used': columns_used,
                'visualizations': visualizations
            }
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            logger.error(f"Code execution error: {error_msg}")
            
            return {
                'success': False,
                'result': None,
                'output': captured_output.getvalue(),
                'error': error_msg,
                'columns_used': list(self.columns_accessed),
                'visualizations': visualizations
            }
            
        finally:
            sys.stdout = old_stdout
            plt.close('all')
    
    def _create_tracked_dataframe(self, df: pd.DataFrame):
        """
        Create a DataFrame wrapper that tracks column access
        """
        class TrackedDataFrame:
            def __init__(self, dataframe, executor):
                self._df = dataframe
                self._executor = executor
            
            def __getitem__(self, key):
                # Track column access
                if isinstance(key, str):
                    self._executor.columns_accessed.add(key)
                elif isinstance(key, list):
                    for k in key:
                        if isinstance(k, str):
                            self._executor.columns_accessed.add(k)
                return self._df[key]
            
            def __getattr__(self, name):
                # Forward all other attributes to the original DataFrame
                return getattr(self._df, name)
            
            def __repr__(self):
                return repr(self._df)
            
            def __str__(self):
                return str(self._df)
        
        return TrackedDataFrame(df, self)
    
    def validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for safety (basic checks)
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # List of potentially dangerous operations
        dangerous_patterns = [
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'__import__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'compile\s*\(',
            r'open\s*\(',
            r'file\s*\(',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Code contains potentially unsafe operation: {pattern}"
        
        # Try to compile the code
        try:
            compile(code, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
    
    def extract_columns_from_code(self, code: str) -> List[str]:
        """
        Statically analyze code to extract column references
        
        Args:
            code: Python code
            
        Returns:
            List of column names referenced in code
        """
        columns = []
        
        # Pattern for df['column'] or df["column"]
        pattern1 = r"df\s*\[\s*['\"]([^'\"]+)['\"]\s*\]"
        columns.extend(re.findall(pattern1, code))
        
        # Pattern for df[['col1', 'col2']]
        pattern2 = r"df\s*\[\s*\[([^\]]+)\]\s*\]"
        matches = re.findall(pattern2, code)
        for match in matches:
            # Extract individual column names
            cols = re.findall(r"['\"]([^'\"]+)['\"]", match)
            columns.extend(cols)
        
        return list(set(columns))  # Remove duplicates
    
    def format_result(self, result: Any) -> Dict[str, Any]:
        """
        Format execution result for display
        
        Args:
            result: Execution result
            
        Returns:
            Formatted result dictionary
        """
        if result is None:
            return {'type': 'none', 'display': 'No result'}
        
        if isinstance(result, pd.DataFrame):
            return {
                'type': 'dataframe',
                'display': result.to_html(index=False, classes='table table-striped'),
                'data': result.to_dict('records'),
                'shape': result.shape
            }
        
        elif isinstance(result, pd.Series):
            return {
                'type': 'series',
                'display': result.to_frame().to_html(classes='table table-striped'),
                'data': result.to_dict(),
            }
        
        elif isinstance(result, (list, tuple)):
            return {
                'type': 'list',
                'display': str(result),
                'data': list(result)
            }
        
        elif isinstance(result, dict):
            return {
                'type': 'dict',
                'display': str(result),
                'data': result
            }
        
        elif isinstance(result, (int, float, str, bool)):
            return {
                'type': 'scalar',
                'display': str(result),
                'data': result
            }
        
        else:
            return {
                'type': 'other',
                'display': str(result),
                'data': str(result)
            }
    
    def create_execution_report(self, query: str, code: str, 
                               execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a comprehensive execution report
        
        Args:
            query: Original user query
            code: Executed code
            execution_result: Result from execute_code
            
        Returns:
            Comprehensive report dictionary
        """
        report = {
            'query': query,
            'code': code,
            'success': execution_result['success'],
            'columns_used': execution_result['columns_used'],
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        if execution_result['success']:
            report['result'] = self.format_result(execution_result['result'])
            report['output'] = execution_result['output']
            report['visualizations'] = execution_result['visualizations']
        else:
            report['error'] = execution_result['error']
            report['output'] = execution_result['output']
        
        return report


def execute_analysis(code: str, data_path: str) -> Dict[str, Any]:
    """
    Convenience function to execute analysis code
    
    Args:
        code: Python code to execute
        data_path: Path to data file
        
    Returns:
        Execution report
    """
    # Load data
    if data_path.endswith('.csv'):
        df = pd.read_csv(data_path)
    elif data_path.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(data_path)
    else:
        raise ValueError(f"Unsupported file format: {data_path}")
    
    # Execute code
    executor = CodeExecutor()
    result = executor.execute_code(code, df)
    
    return result

