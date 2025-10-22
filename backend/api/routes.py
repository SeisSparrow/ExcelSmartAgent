"""
REST API Routes
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import shutil
from pathlib import Path
import logging

from backend.config import settings
from backend.core.excel_processor import process_excel_file
from backend.core.llm_agent import LLMAgent
from backend.core.code_executor import execute_analysis
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    file_name: Optional[str] = None


class CodeExecutionRequest(BaseModel):
    code: str
    file_path: str


@router.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirect to docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")

@router.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Excel Smart Agent API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "health": "/api/health",
            "upload": "/api/upload",
            "files": "/api/files",
            "websocket": "ws://localhost:8000/ws"
        }
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload Excel file for processing
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。允许的格式: {', '.join(settings.allowed_extensions)}"
            )
        
        # Save uploaded file
        file_path = settings.excel_data_path / file.filename
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file
        result = process_excel_file(str(file_path), str(settings.processed_data_path))
        
        return {
            "success": True,
            "message": "文件上传并处理成功",
            "file_name": file.filename,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files")
async def list_files():
    """
    List all processed files
    """
    try:
        files = []
        
        # List Excel files
        for file_path in settings.excel_data_path.glob("*"):
            if file_path.suffix in settings.allowed_extensions:
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "size": file_path.stat().st_size,
                    "type": "excel"
                })
        
        # List processed CSV files
        for file_path in settings.processed_data_path.glob("*.csv"):
            files.append({
                "name": file_path.name,
                "path": str(file_path),
                "size": file_path.stat().st_size,
                "type": "processed"
            })
        
        return {
            "success": True,
            "files": files,
            "count": len(files)
        }
        
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query")
async def process_query(request: QueryRequest):
    """
    Process natural language query (REST API version)
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="查询内容不能为空")
        
        # This is a simplified version for REST API
        # For full functionality, use WebSocket connection
        return {
            "success": True,
            "message": "请使用WebSocket连接以获得完整的实时分析功能",
            "query": query,
            "websocket_url": f"ws://{settings.host}:{settings.port}/ws"
        }
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute")
async def execute_code(request: CodeExecutionRequest):
    """
    Execute Python code against data file
    """
    try:
        result = execute_analysis(request.code, request.file_path)
        
        return {
            "success": result['success'],
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error executing code: {e}")
        raise HTTPException(status_code=500, detail=str(e))

