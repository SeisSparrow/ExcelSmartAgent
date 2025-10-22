"""
WebSocket Handler Module
Handles real-time WebSocket connections for voice input and analysis
"""
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Any
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
import glob

from backend.core.excel_processor import ExcelProcessor
from backend.core.llm_agent import LLMAgent
from backend.core.code_executor import CodeExecutor
from backend.utils.audio_processor import AudioProcessor
from backend.config import settings
import pandas as pd

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_data: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept and store new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_data[websocket] = {
            'connected_at': datetime.now().isoformat(),
            'session_id': id(websocket)
        }
        logger.info(f"New WebSocket connection: {id(websocket)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            if websocket in self.connection_data:
                del self.connection_data[websocket]
        logger.info(f"WebSocket disconnected: {id(websocket)}")
    
    async def send_message(self, message: Dict, websocket: WebSocket):
        """Send message to specific connection"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connections"""
        for connection in self.active_connections:
            await self.send_message(message, connection)


class WebSocketHandler:
    """Handle WebSocket messages and process analysis requests"""
    
    def __init__(self):
        self.manager = ConnectionManager()
        self.llm_agent = LLMAgent()
        self.audio_processor = AudioProcessor()
        self.executor = CodeExecutor()
        
        # Cache for processed files
        self.processed_files: Dict[str, pd.DataFrame] = {}
        self.file_metadata: Dict[str, Dict] = {}
    
    async def handle_connection(self, websocket: WebSocket):
        """Handle WebSocket connection lifecycle"""
        await self.manager.connect(websocket)
        
        try:
            # Send welcome message
            await self.manager.send_message({
                'type': 'connection',
                'status': 'connected',
                'message': '连接成功！您可以发送文本或语音查询。'
            }, websocket)
            
            # Message loop
            while True:
                # Receive message
                data = await websocket.receive()
                
                if 'text' in data:
                    message = json.loads(data['text'])
                    await self.handle_text_message(message, websocket)
                elif 'bytes' in data:
                    await self.handle_audio_message(data['bytes'], websocket)
                    
        except WebSocketDisconnect:
            self.manager.disconnect(websocket)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await self.manager.send_message({
                'type': 'error',
                'message': f'服务器错误: {str(e)}'
            }, websocket)
            self.manager.disconnect(websocket)
    
    async def handle_text_message(self, message: Dict, websocket: WebSocket):
        """Handle text-based messages"""
        msg_type = message.get('type')
        
        if msg_type == 'query':
            # Process analysis query
            query = message.get('query', '').strip()
            if not query:
                await self.manager.send_message({
                    'type': 'error',
                    'message': '查询内容不能为空'
                }, websocket)
                return
            
            await self.process_query(query, websocket)
            
        elif msg_type == 'upload_file':
            # Handle file upload notification
            file_info = message.get('file_info')
            await self.process_file(file_info, websocket)
            
        elif msg_type == 'list_files':
            # List available files
            await self.list_files(websocket)
            
        elif msg_type == 'ping':
            # Respond to ping
            await self.manager.send_message({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            }, websocket)
            
        else:
            await self.manager.send_message({
                'type': 'error',
                'message': f'未知的消息类型: {msg_type}'
            }, websocket)
    
    async def handle_audio_message(self, audio_data: bytes, websocket: WebSocket):
        """Handle audio data and convert to text query"""
        # Send acknowledgment
        await self.manager.send_message({
            'type': 'status',
            'message': '正在处理语音...'
        }, websocket)
        
        # Convert audio to text
        text = self.audio_processor.audio_to_text(audio_data)
        
        if text:
            # Send transcription
            await self.manager.send_message({
                'type': 'transcription',
                'text': text,
                'message': f'识别结果: {text}'
            }, websocket)
            
            # Process as query
            await self.process_query(text, websocket)
        else:
            await self.manager.send_message({
                'type': 'error',
                'message': '无法识别语音，请重试'
            }, websocket)
    
    async def process_query(self, query: str, websocket: WebSocket):
        """Process analysis query"""
        try:
            # Send status update
            await self.manager.send_message({
                'type': 'status',
                'message': '正在分析查询...',
                'step': 'understanding'
            }, websocket)
            
            # Get available data
            available_data = self._get_available_data()
            
            if not available_data:
                await self.manager.send_message({
                    'type': 'error',
                    'message': '没有可用的数据文件，请先上传Excel文件'
                }, websocket)
                return
            
            # Select relevant files
            file_info_list = [
                {
                    'name': name,
                    'path': name,
                    'columns': meta.get('columns', []),
                    'preview': str(meta.get('preview', ''))
                }
                for name, meta in self.file_metadata.items()
            ]
            
            selected_files = self.llm_agent.select_relevant_files(query, file_info_list)
            
            if not selected_files:
                selected_files = list(self.processed_files.keys())[:1]
            
            # Get the first selected file's data
            file_name = selected_files[0]
            df = self.processed_files.get(file_name)
            
            if df is None:
                await self.manager.send_message({
                    'type': 'error',
                    'message': '无法加载数据'
                }, websocket)
                return
            
            # Understand query
            data_info = {
                'file_name': file_name,
                'columns': list(df.columns),
                'shape': df.shape,
                'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
                'preview': df.head(3).to_dict('records')
            }
            
            analysis_plan = self.llm_agent.understand_query(query, data_info)
            
            await self.manager.send_message({
                'type': 'analysis_plan',
                'plan': analysis_plan,
                'message': '分析计划已生成'
            }, websocket)
            
            # Generate code
            await self.manager.send_message({
                'type': 'status',
                'message': '正在生成代码...',
                'step': 'code_generation'
            }, websocket)
            
            code_result = self.llm_agent.generate_code(query, data_info, analysis_plan)
            
            await self.manager.send_message({
                'type': 'code_generated',
                'code': code_result.get('code', ''),
                'explanation': code_result.get('explanation', ''),
                'message': '代码已生成'
            }, websocket)
            
            # Execute code
            await self.manager.send_message({
                'type': 'status',
                'message': '正在执行代码...',
                'step': 'execution'
            }, websocket)
            
            execution_result = self.executor.execute_code(
                code_result['code'],
                df
            )
            
            if execution_result['success']:
                # Format result
                formatted_result = self.executor.format_result(execution_result['result'])
                
                # Create summary
                summary = self.llm_agent.create_summary(
                    query,
                    code_result['code'],
                    execution_result['result'],
                    execution_result['columns_used']
                )
                
                # Send complete result
                await self.manager.send_message({
                    'type': 'result',
                    'success': True,
                    'query': query,
                    'code': code_result['code'],
                    'result': formatted_result,
                    'summary': summary,
                    'columns_used': execution_result['columns_used'],
                    'visualizations': execution_result['visualizations'],
                    'output': execution_result['output']
                }, websocket)
            else:
                await self.manager.send_message({
                    'type': 'result',
                    'success': False,
                    'error': execution_result['error'],
                    'message': '代码执行失败'
                }, websocket)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            await self.manager.send_message({
                'type': 'error',
                'message': f'处理查询时出错: {str(e)}'
            }, websocket)
    
    async def process_file(self, file_info: Dict, websocket: WebSocket):
        """Load already processed Excel file data into memory"""
        try:
            file_name = file_info.get('path') or file_info.get('name')
            
            await self.manager.send_message({
                'type': 'status',
                'message': '正在加载文件数据...'
            }, websocket)
            
            # Look for processed CSV files
            processed_pattern = settings.processed_data_path / f"{Path(file_name).stem}_*.csv"
            csv_files = list(glob.glob(str(processed_pattern)))
            
            if not csv_files:
                # File not processed yet, process it now
                file_path = settings.excel_data_path / file_name
                
                if not file_path.exists():
                    await self.manager.send_message({
                        'type': 'error',
                        'message': f'文件不存在: {file_name}'
                    }, websocket)
                    return
                
                # Process Excel file
                processor = ExcelProcessor(str(file_path))
                result = processor.process_and_save(settings.processed_data_path)
            else:
                # File already processed, just load it
                result = {'file_name': file_name, 'sheets': {}}
                
                for csv_file in csv_files:
                    sheet_name = Path(csv_file).stem.replace(f"{Path(file_name).stem}_", "")
                    df = pd.read_csv(csv_file)
                    
                    result['sheets'][sheet_name] = {
                        'output_file': csv_file,
                        'row_count': len(df),
                        'column_count': len(df.columns),
                        'columns': list(df.columns)
                    }
            
            # Load processed data into memory
            for sheet_name, sheet_info in result['sheets'].items():
                output_file = sheet_info['output_file']
                df = pd.read_csv(output_file)
                
                key = f"{Path(file_name).stem}_{sheet_name}"
                self.processed_files[key] = df
                self.file_metadata[key] = sheet_info
            
            await self.manager.send_message({
                'type': 'file_processed',
                'result': result,
                'message': f'文件加载完成！共 {len(result["sheets"])} 个工作表'
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error processing file: {e}", exc_info=True)
            await self.manager.send_message({
                'type': 'error',
                'message': f'文件处理失败: {str(e)}'
            }, websocket)
    
    async def list_files(self, websocket: WebSocket):
        """List available files"""
        files = [
            {
                'name': name,
                'columns': meta.get('columns', []),
                'row_count': meta.get('row_count', 0),
                'column_count': meta.get('column_count', 0)
            }
            for name, meta in self.file_metadata.items()
        ]
        
        await self.manager.send_message({
            'type': 'file_list',
            'files': files
        }, websocket)
    
    def _get_available_data(self) -> Dict[str, pd.DataFrame]:
        """Get available data files"""
        return self.processed_files

