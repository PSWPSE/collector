# 🌐 **NewsForge Pro 클라우드 배포 가이드**

## 🎯 **배포 옵션 비교**

### **Option 1: 빠른 배포 (1-2시간)**
```yaml
Frontend: Vercel (Next.js 특화)
Backend: Railway / Render (FastAPI 지원)
Database: PostgreSQL (관리형)
비용: $10-30/월
난이도: ⭐⭐☆☆☆
```

### **Option 2: 중간 배포 (1-2일)**
```yaml
Frontend + Backend: DigitalOcean App Platform
Database: DigitalOcean Managed Database
비용: $20-50/월
난이도: ⭐⭐⭐☆☆
```

### **Option 3: 전문 배포 (1-2주)**
```yaml
Infrastructure: AWS (ECS, RDS, CloudFront)
CI/CD: GitHub Actions
Monitoring: CloudWatch
비용: $50-200/월
난이도: ⭐⭐⭐⭐⭐
```

## 🚀 **Option 1: 빠른 배포 (권장)**

### **1. Vercel 배포 (Frontend)**
```bash
# 1. Vercel CLI 설치
npm install -g vercel

# 2. 프로젝트 배포
cd news-to-social-web
vercel

# 3. 환경 변수 설정
vercel env add FASTAPI_URL
# 값: https://your-backend-app.up.railway.app

# 4. 프로덕션 배포
vercel --prod
```

### **2. Railway 배포 (Backend)**
```yaml
# railway.json
{
  "name": "newsforge-pro-api",
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/api/v1/health",
    "healthcheckTimeout": 30
  }
}
```

### **3. 환경 변수 설정**
```bash
# Railway 환경 변수
DATABASE_URL=postgresql://user:pass@host:5432/db
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

## 📋 **단계별 배포 가이드**

### **Step 1: 코드 준비**
```bash
# 1. GitHub 리포지토리 생성
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/newsforge-pro.git
git push -u origin main

# 2. 프로덕션 환경 설정
cp .env.example .env.production
```

### **Step 2: Database 설정**
```bash
# PostgreSQL 스키마 생성
CREATE DATABASE newsforge_prod;

-- 사용자 테이블
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 변환 로그 테이블
CREATE TABLE conversions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    source_url TEXT NOT NULL,
    generated_content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Step 3: Backend 배포**
```bash
# Railway 배포
railway login
railway init
railway up

# 또는 Render 배포
# 1. Render.com에서 새 웹 서비스 생성
# 2. GitHub 리포지토리 연결
# 3. 빌드 명령어: pip install -r requirements.txt
# 4. 시작 명령어: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### **Step 4: Frontend 배포**
```bash
# Vercel 배포
cd news-to-social-web
vercel

# 환경 변수 설정
vercel env add NEXT_PUBLIC_API_URL
# 값: https://your-backend-app.up.railway.app
```

## 🔧 **프로덕션 환경 최적화**

### **FastAPI 프로덕션 설정**
```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import logging
import os

app = FastAPI(
    title="NewsForge Pro API",
    description="News to Social Media Content Converter",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") == "development" else None,
    redoc_url=None
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 압축 미들웨어
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.on_event("startup")
async def startup_event():
    logging.info("🚀 NewsForge Pro API starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logging.info("🛑 NewsForge Pro API shutting down...")
```

### **환경별 설정**
```python
# app/config/settings.py
from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # API Keys
    openai_api_key: str
    anthropic_api_key: str
    
    # CORS
    cors_origins: List[str] = []
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Security
    secret_key: str
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 💰 **배포 옵션별 비용 분석**

### **Option 1: 빠른 배포**
```yaml
Vercel (Frontend):
  - Hobby: $0/월 (제한적)
  - Pro: $20/월 (상용 서비스)

Railway (Backend):
  - Starter: $5/월 (500시간)
  - Developer: $10/월 (무제한)

PostgreSQL:
  - Railway: $5/월 (1GB)
  - Supabase: $25/월 (8GB)

총 비용: $10-50/월
```

### **Option 2: 중간 배포**
```yaml
DigitalOcean:
  - App Platform: $12/월 (Basic)
  - Managed Database: $15/월 (1GB)
  - CDN: $5/월

총 비용: $32/월
```

### **Option 3: 전문 배포**
```yaml
AWS:
  - ECS Fargate: $30-100/월
  - RDS PostgreSQL: $20-50/월
  - CloudFront: $10-30/월
  - Load Balancer: $20/월

총 비용: $80-200/월
```

## 🛠️ **즉시 실행 가능한 배포 스크립트**

### **자동 배포 스크립트**
```bash
#!/bin/bash
# deploy.sh

echo "🚀 NewsForge Pro 자동 배포 시작..."

# 1. 환경 확인
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production 파일이 없습니다."
    exit 1
fi

# 2. 의존성 확인
echo "📦 의존성 확인 중..."
pip install -r requirements.txt
cd news-to-social-web && npm install && cd ..

# 3. 테스트 실행
echo "🧪 테스트 실행 중..."
python -m pytest tests/ -v
if [ $? -ne 0 ]; then
    echo "❌ 테스트 실패"
    exit 1
fi

# 4. 빌드
echo "🏗️ 빌드 중..."
cd news-to-social-web
npm run build
cd ..

# 5. 배포
echo "🚀 배포 중..."
git add .
git commit -m "Deploy: $(date)"
git push origin main

echo "✅ 배포 완료!"
echo "🌐 Frontend: https://your-app.vercel.app"
echo "🔗 Backend: https://your-api.railway.app"
```

## 🔍 **배포 후 확인사항**

### **헬스 체크**
```bash
# API 헬스 체크
curl https://your-api.railway.app/api/v1/health

# 예상 응답
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0",
  "service": "NewsForge Pro API"
}
```

### **기능 테스트**
```bash
# 뉴스 변환 테스트
curl -X POST https://your-api.railway.app/api/v1/convert \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/news",
    "converter_type": "openai"
  }'
```

## 🎯 **추천 배포 전략**

### **단계별 배포**
1. **Phase 1**: Railway + Vercel (빠른 시작)
2. **Phase 2**: DigitalOcean (비용 최적화)
3. **Phase 3**: AWS (확장성 극대화)

### **모니터링 설정**
```python
# 헬스 체크 엔드포인트
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "NewsForge Pro API",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# 메트릭 엔드포인트
@app.get("/api/v1/metrics")
async def get_metrics():
    return {
        "total_conversions": await get_total_conversions(),
        "active_users": await get_active_users(),
        "uptime": get_uptime()
    }
```

---

**🎯 결론: 현재는 로컬 환경이므로 PC가 꺼지면 서비스가 중단됩니다. 24/7 서비스를 위해서는 클라우드 배포가 필요합니다.**

**가장 빠른 방법: Railway + Vercel 조합으로 1-2시간 내에 배포 가능합니다!** 