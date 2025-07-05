#!/usr/bin/env python3
"""
NewsForge Pro API Server Starter
Production-ready FastAPI server with proper error handling and logging
"""

import uvicorn
import logging
import sys
import os
from pathlib import Path

# 프로젝트 루트 경로 설정
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """FastAPI 서버 시작"""
    try:
        logger.info("🚀 Starting NewsForge Pro API Server...")
        
        # 환경 변수 확인
        logger.info(f"Python Path: {sys.path}")
        logger.info(f"Current Working Directory: {os.getcwd()}")
        logger.info(f"Project Root: {project_root}")
        
        # Uvicorn 서버 시작
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            workers=2,
            log_level="info",
            access_log=True,
            reload=False  # 프로덕션에서는 False
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to start API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 