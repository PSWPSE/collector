"""
간소화된 NewsForge Pro FastAPI 애플리케이션
모든 중복 코드 제거 및 직접 연결 구조
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
import uvicorn

# 통합 서비스 import
from .services.unified_converter import get_unified_converter, convert_news_unified, validate_user_api_key
from .config.api_keys import get_all_available_keys


# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Pydantic 모델들
class ConversionRequest(BaseModel):
    url: HttpUrl
    title: str
    content: str
    provider: str = 'openai'
    user_api_key: Optional[str] = None


class ApiKeyValidationRequest(BaseModel):
    provider: str
    api_key: str


class ConversionResponse(BaseModel):
    id: str
    url: str
    original_title: str
    markdown_content: str
    provider: str
    processing_time_seconds: float
    timestamp: str
    success: bool
    token_usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


# 애플리케이션 라이프사이클
@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 관리"""
    logger.info("🚀 NewsForge Pro Unified API Starting...")
    
    # 서비스 초기화
    converter = get_unified_converter()
    service_info = converter.get_service_info()
    logger.info(f"✅ {service_info['name']} v{service_info['version']} initialized")
    
    # API 키 상태 확인
    key_status = get_all_available_keys()
    for provider, status in key_status.items():
        if status['available']:
            logger.info(f"✅ {provider.upper()} API key ready")
        else:
            logger.warning(f"⚠️  {provider.upper()} API key not available")
    
    yield
    
    logger.info("🛑 NewsForge Pro Unified API Shutting down...")


# FastAPI 앱 초기화
app = FastAPI(
    title="NewsForge Pro Unified API",
    description="간소화된 뉴스-마크다운 변환 서비스",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://collector-2xwdc12kl-dsvsdvsdvsds-projects.vercel.app",
        "https://collector-b7ilffdp8-dsvsdvsdvsds-projects.vercel.app",
        "https://nongbux-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 요청 ID 미들웨어
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """모든 요청에 고유 ID 추가"""
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    
    return response


# 헬스 체크 엔드포인트
@app.get("/api/v1/health")
async def health_check():
    """서비스 상태 확인"""
    converter = get_unified_converter()
    service_info = converter.get_service_info()
    key_status = get_all_available_keys()
    
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": service_info,
        "api_keys": key_status
    }


# 메인 변환 엔드포인트
@app.post("/api/v1/convert", response_model=ConversionResponse)
async def convert_news_endpoint(
    request: ConversionRequest,
    background_tasks: BackgroundTasks
):
    """뉴스 기사를 마크다운으로 변환"""
    try:
        logger.info(f"🔄 Converting: {request.url}")
        
        # 통합 서비스로 변환
        result = await convert_news_unified(
            url=str(request.url),
            title=request.title,
            content=request.content,
            provider=request.provider,
            user_api_key=request.user_api_key
        )
        
        # 백그라운드 태스크로 사용량 로깅 (필요시)
        background_tasks.add_task(log_usage, result)
        
        return ConversionResponse(**result)
        
    except ValueError as e:
        logger.error(f"❌ Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Conversion failed: {str(e)}")
        raise HTTPException(status_code=500, detail="내부 서버 오류가 발생했습니다")


# API 키 검증 엔드포인트
@app.post("/api/v1/validate-key")
async def validate_api_key_endpoint(request: ApiKeyValidationRequest):
    """사용자 API 키 검증"""
    try:
        result = await validate_user_api_key(request.provider, request.api_key)
        
        if result['valid']:
            return {
                "success": True,
                "message": "API 키가 유효합니다",
                "provider": request.provider
            }
        else:
            return {
                "success": False,
                "message": result.get('error', 'API 키가 유효하지 않습니다'),
                "provider": request.provider
            }
            
    except Exception as e:
        logger.error(f"❌ API key validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="API 키 검증 중 오류가 발생했습니다")


# 지원되는 제공자 목록
@app.get("/api/v1/providers")
async def get_supported_providers():
    """지원되는 AI 제공자 목록"""
    converter = get_unified_converter()
    return {
        "providers": converter.get_supported_providers(),
        "default": "openai"
    }


# 서비스 정보
@app.get("/api/v1/info")
async def get_service_info():
    """서비스 정보 반환"""
    converter = get_unified_converter()
    return converter.get_service_info()


# 백그라운드 태스크들
async def log_usage(conversion_result: Dict[str, Any]):
    """사용량 로깅 (백그라운드 태스크)"""
    try:
        # 여기에 사용량 로깅 로직 추가
        logger.info(f"📊 Usage logged for conversion {conversion_result['id']}")
    except Exception as e:
        logger.error(f"❌ Usage logging failed: {str(e)}")


# 에러 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP 예외 핸들러"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """일반 예외 핸들러"""
    logger.error(f"❌ Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "내부 서버 오류가 발생했습니다",
            "status_code": 500,
            "timestamp": datetime.now().isoformat(),
            "request_id": getattr(request.state, 'request_id', 'unknown')
        }
    )


# 개발 서버 실행
if __name__ == "__main__":
    uvicorn.run(
        "main_simplified:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    ) 