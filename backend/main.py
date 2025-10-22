"""
Main FastAPI Application
"""
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging
import sys

from backend.config import settings
from backend.api.routes import router
from backend.api.websocket_handler import WebSocketHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(settings.log_path / 'app.log')
    ]
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Excel Smart Agent",
    description="智能Excel数据分析系统，支持自然语言查询和语音输入",
    version="1.0.0",
    debug=settings.debug
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST API routes
app.include_router(router, prefix="/api", tags=["api"])

# WebSocket handler
ws_handler = WebSocketHandler()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await ws_handler.handle_connection(websocket)


# Serve static files (frontend)
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    try:
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="static")
    except Exception as e:
        logger.warning(f"Could not mount static files: {e}")


@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("Starting Excel Smart Agent...")
    logger.info(f"Data path: {settings.excel_data_path}")
    logger.info(f"Processed data path: {settings.processed_data_path}")
    logger.info(f"Log path: {settings.log_path}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("Shutting down Excel Smart Agent...")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info" if settings.debug else "warning"
    )

