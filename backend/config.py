"""
Configuration module for Excel Smart Agent
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = {
        "protected_namespaces": (),  # Fix Pydantic warning
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    # API Keys
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Model Configuration
    llm_provider: str = "openai"
    model_name: str = "gpt-4-turbo-preview"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # File Configuration
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_extensions: list = [".xlsx", ".xls", ".csv"]
    
    # Paths
    base_dir: Path = Path(__file__).parent.parent
    excel_data_path: Path = base_dir / "data" / "excel_files"
    processed_data_path: Path = base_dir / "data" / "processed"
    log_path: Path = base_dir / "logs"


# Global settings instance
settings = Settings()

# Ensure directories exist
settings.excel_data_path.mkdir(parents=True, exist_ok=True)
settings.processed_data_path.mkdir(parents=True, exist_ok=True)
settings.log_path.mkdir(parents=True, exist_ok=True)

