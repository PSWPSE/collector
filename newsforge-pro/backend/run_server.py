#!/usr/bin/env python3
"""
NewsForge Pro 개발 서버 실행 스크립트
"""

import uvicorn
import os
import sys
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """메인 서버 실행"""
    
    # 환경 변수 설정
    os.environ.setdefault("ENVIRONMENT", "development")
    
    print("🚀 NewsForge Pro 개발 서버 시작")
    print("📍 API 문서: http://localhost:8000/api/docs")
    print("🔧 환경: 개발 모드")
    print("=" * 50)
    
    # uvicorn 서버 실행
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # 개발 모드에서 자동 리로드
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 