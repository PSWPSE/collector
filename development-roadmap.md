# NewsForge Pro - 단계별 개발 로드맵

## 🚀 Phase 1: 핵심 인프라 구축 (1-2주)

### 1.1 개발환경 셋팅
```bash
# 프로젝트 초기화
mkdir newsforge-pro
cd newsforge-pro

# 백엔드 셋팅
mkdir -p backend/app/{config,core,models,api,services,schemas,utils}
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install uv
uv pip install fastapi uvicorn sqlalchemy asyncpg redis pydantic python-jose

# 프론트엔드 셋팅
cd ../
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install zustand @tanstack/react-query axios

# Docker 환경
cd ../
mkdir -p infrastructure/docker
```

### 1.2 핵심 설정 파일 생성
```python
# backend/app/config/settings.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://user:pass@localhost/newsforge"
    redis_url: str = "redis://localhost:6379"
    jwt_secret_key: str = "your-secret-key"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 1.3 Docker Compose 셋업
```yaml
# infrastructure/docker/docker-compose.yml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: newsforge
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build: ../../backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis

  frontend:
    build: ../../frontend
    ports:
      - "3000:3000"

volumes:
  postgres_data:
```

## 🔧 Phase 2: 백엔드 API 개발 (2-3주)

### 2.1 데이터베이스 모델
```python
# backend/app/models/user.py
from sqlalchemy import Column, String, Boolean, Integer
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    daily_usage = Column(Integer, default=0)
```

### 2.2 인증 시스템
```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from ..dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
async def register(user_data: UserCreate):
    # 사용자 등록 로직
    pass

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm):
    # 로그인 로직
    pass
```

### 2.3 변환 서비스
```python
# backend/app/services/converters/base.py
from abc import ABC, abstractmethod

class BaseConverter(ABC):
    @abstractmethod
    async def convert(self, content: str, platform: str) -> str:
        pass

# backend/app/services/converters/openai_converter.py
class OpenAIConverter(BaseConverter):
    async def convert(self, content: str, platform: str) -> str:
        # OpenAI API 호출 로직
        pass
```

## 🎨 Phase 3: 프론트엔드 개발 (2-3주)

### 3.1 상태 관리 설정
```typescript
// frontend/src/store/auth-store.ts
import { create } from 'zustand'

interface AuthState {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  login: async (email, password) => {
    // 로그인 로직
  },
  logout: () => set({ user: null, token: null })
}))
```

### 3.2 API 클라이언트
```typescript
// frontend/src/lib/api.ts
import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
})

export const authAPI = {
  login: (email: string, password: string) => 
    api.post('/auth/login', { email, password }),
  register: (userData: RegisterData) => 
    api.post('/auth/register', userData)
}

export const converterAPI = {
  convert: (url: string, platform: string) => 
    api.post('/convert', { url, platform })
}
```

### 3.3 핵심 컴포넌트
```tsx
// frontend/src/components/converter/url-input.tsx
'use client'

export function UrlInput() {
  const [url, setUrl] = useState('')
  const [platform, setPlatform] = useState('twitter')
  
  return (
    <div className="space-y-4">
      <input 
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="뉴스 기사 URL을 입력하세요"
        className="w-full p-3 border rounded-lg"
      />
      <select 
        value={platform}
        onChange={(e) => setPlatform(e.target.value)}
        className="w-full p-3 border rounded-lg"
      >
        <option value="twitter">X (Twitter)</option>
        <option value="threads">Threads</option>
        <option value="linkedin">LinkedIn</option>
      </select>
    </div>
  )
}
```

## 🔄 Phase 4: 통합 및 최적화 (1-2주)

### 4.1 캐싱 시스템
```python
# backend/app/services/cache_service.py
import redis.asyncio as redis
import json

class CacheService:
    def __init__(self):
        self.redis = redis.from_url("redis://localhost:6379")
    
    async def get(self, key: str):
        data = await self.redis.get(key)
        return json.loads(data) if data else None
    
    async def set(self, key: str, value: dict, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(value))
```

### 4.2 에러 처리
```python
# backend/app/core/exceptions.py
from fastapi import HTTPException

class NewsExtractionError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=422,
            detail="뉴스 기사를 추출할 수 없습니다"
        )

class ConversionError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=500,
            detail="변환 중 오류가 발생했습니다"
        )
```

### 4.3 모니터링
```python
# backend/app/core/middleware.py
import time
from fastapi import Request

async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🚢 Phase 5: 배포 및 운영 (1주)

### 5.1 Nginx 설정
```nginx
# infrastructure/nginx/nginx.conf
upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name localhost;

    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
    }
}
```

### 5.2 환경 변수 관리
```bash
# .env.template
DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/newsforge
REDIS_URL=redis://redis:6379
JWT_SECRET_KEY=your-jwt-secret
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
NEXT_PUBLIC_API_URL=http://localhost/api
```

### 5.3 건강 검사
```python
# backend/app/api/v1/health.py
@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

## 📊 성능 목표

```yaml
Performance Targets:
  - 응답 시간: < 5초 (95th percentile)
  - 가용성: > 99.9%
  - 동시 사용자: 1000+
  - 일일 변환: 10,000+

Quality Metrics:
  - 테스트 커버리지: > 80%
  - 코드 품질: A등급
  - 보안 스캔: 취약점 0개
  - 성능 점수: > 90점
```

## 🔧 개발 도구 및 명령어

```bash
# 개발 시작
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# 백엔드 개발 서버
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 프론트엔드 개발 서버
cd frontend && npm run dev

# 테스트 실행
cd backend && pytest tests/ -v
cd frontend && npm test

# 타입 체크
cd backend && mypy app/
cd frontend && npm run type-check

# 코드 포맷팅
cd backend && black app/ && isort app/
cd frontend && npm run lint:fix
```

이 로드맵을 따르면 안정적이고 확장 가능한 프로덕션 서비스를 구축할 수 있습니다. 