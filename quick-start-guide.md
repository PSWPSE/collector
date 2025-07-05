# NewsForge Pro - 퀵스타트 가이드

## 🚀 30분만에 시작하기

### 1단계: 프로젝트 초기화 (5분)

```bash
# 1. 프로젝트 구조 생성
mkdir newsforge-pro
cd newsforge-pro

# 2. 기본 디렉토리 생성
mkdir -p {backend,frontend,infrastructure/{docker,nginx},docs,scripts}

# 3. Git 초기화
git init
echo "venv/\n.env\nnode_modules/\n*.pyc\n.next/" > .gitignore
```

### 2단계: 백엔드 설정 (10분)

```bash
# 1. FastAPI 프로젝트 생성
cd backend
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. 의존성 설치 (최신 버전)
pip install uv
uv pip install \
  fastapi==0.104.1 \
  uvicorn[standard]==0.24.0 \
  sqlalchemy==2.0.23 \
  asyncpg==0.29.0 \
  redis==5.0.1 \
  pydantic==2.5.0 \
  python-jose[cryptography]==3.3.0 \
  python-multipart==0.0.6 \
  bcrypt==4.1.2 \
  openai==1.3.7 \
  anthropic==0.8.1

# 3. 개발 의존성
uv pip install \
  pytest==7.4.3 \
  pytest-asyncio==0.21.1 \
  httpx==0.25.2 \
  black==23.11.0 \
  isort==5.12.0 \
  mypy==1.7.1
```

### 3단계: 핵심 백엔드 파일 생성 (10분)

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, convert, health

app = FastAPI(title="NewsForge Pro API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(convert.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "NewsForge Pro API"}
```

```python
# backend/app/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://newsforge:password@localhost:5432/newsforge_db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # AI APIs
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # App settings
    app_name: str = "NewsForge Pro"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

```python
# backend/app/api/v1/convert.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.converters.factory import ConverterFactory
from app.services.extractors.web_extractor import WebExtractor

router = APIRouter(prefix="/convert", tags=["convert"])

class ConvertRequest(BaseModel):
    url: str
    platform: str  # twitter, threads, linkedin
    ai_provider: str = "openai"  # openai, anthropic

class ConvertResponse(BaseModel):
    original_content: str
    converted_content: str
    platform: str
    processing_time: float

@router.post("/", response_model=ConvertResponse)
async def convert_news(request: ConvertRequest):
    try:
        # 1. 뉴스 추출
        extractor = WebExtractor()
        content = await extractor.extract(request.url)
        
        # 2. AI 변환
        converter = ConverterFactory.create(request.ai_provider)
        converted = await converter.convert(content, request.platform)
        
        return ConvertResponse(
            original_content=content,
            converted_content=converted,
            platform=request.platform,
            processing_time=1.5  # 실제 시간 측정 로직 추가
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 4단계: 프론트엔드 설정 (5분)

```bash
# 1. Next.js 프로젝트 생성
cd ../frontend
npx create-next-app@latest . --typescript --tailwind --app --src-dir

# 2. 추가 의존성 설치
npm install \
  zustand \
  @tanstack/react-query \
  axios \
  @hookform/resolvers \
  react-hook-form \
  zod \
  lucide-react

# 3. 개발 의존성
npm install -D \
  @types/node \
  eslint \
  prettier \
  @playwright/test
```

### 5단계: Docker 설정 (5분)

```yaml
# infrastructure/docker/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: newsforge_db
      POSTGRES_USER: newsforge
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build: 
      context: ../../backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://newsforge:password@postgres:5432/newsforge_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ../../backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ../../frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
    volumes:
      - ../../frontend:/app
      - /app/node_modules
    command: npm run dev

volumes:
  postgres_data:
  redis_data:
```

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install uv && uv pip install --system -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
```

### 6단계: 환경 변수 설정 (2분)

```bash
# backend/.env
DATABASE_URL=postgresql+asyncpg://newsforge:password@localhost:5432/newsforge_db
REDIS_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
DEBUG=True
```

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 7단계: 실행하기 (1분)

```bash
# Docker로 모든 서비스 실행
cd infrastructure/docker
docker-compose up -d

# 또는 개별 실행
# 터미널 1: 백엔드
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 터미널 2: 프론트엔드
cd frontend
npm run dev

# 터미널 3: 데이터베이스 (로컬 설치된 경우)
# PostgreSQL과 Redis 실행
```

### 8단계: 테스트 (2분)

```bash
# API 테스트
curl http://localhost:8000/
curl http://localhost:8000/api/v1/health

# 웹 접속
open http://localhost:3000

# 변환 API 테스트
curl -X POST "http://localhost:8000/api/v1/convert/" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/news-article",
    "platform": "twitter",
    "ai_provider": "openai"
  }'
```

## 🎯 다음 단계

1. **API 키 설정**: OpenAI/Anthropic API 키 발급 및 설정
2. **데이터베이스 마이그레이션**: Alembic 설정 및 테이블 생성
3. **인증 시스템**: JWT 기반 사용자 인증 구현
4. **웹 스크래핑**: BeautifulSoup/Selenium 기반 뉴스 추출
5. **프론트엔드 UI**: 메인 변환 인터페이스 구현

## 🛠️ 개발 명령어

```bash
# 백엔드 테스트
cd backend && pytest tests/ -v

# 프론트엔드 테스트
cd frontend && npm test

# 코드 포맷팅
cd backend && black app/ && isort app/
cd frontend && npm run lint:fix

# 타입 체크
cd backend && mypy app/
cd frontend && npm run type-check

# 빌드
cd backend && python -m build
cd frontend && npm run build
```

이제 기본 구조가 완성되었습니다! 다음은 각 컴포넌트를 하나씩 구현해나가면 됩니다. 