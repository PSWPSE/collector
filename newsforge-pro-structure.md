# NewsForge Pro - 프로덕션 디렉토리 구조

## 📁 전체 프로젝트 구조

```
newsforge-pro/
├── 🏗️ infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.prod.yml
│   │   ├── docker-compose.dev.yml
│   │   └── .env.template
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── sites-enabled/
│   │   │   ├── api.conf
│   │   │   └── frontend.conf
│   │   └── ssl/
│   ├── traefik/
│   │   ├── traefik.yml
│   │   └── dynamic.yml
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana-dashboard.json
├── 🚀 backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   └── database.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── exceptions.py
│   │   │   └── middleware.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── user.py
│   │   │   ├── conversion.py
│   │   │   └── analytics.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py
│   │   │   │   ├── convert.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── health.py
│   │   │   └── dependencies.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── extractors/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── web_extractor.py
│   │   │   │   └── news_sites.py
│   │   │   ├── converters/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base.py
│   │   │   │   ├── openai_converter.py
│   │   │   │   └── anthropic_converter.py
│   │   │   ├── auth_service.py
│   │   │   ├── cache_service.py
│   │   │   └── analytics_service.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── conversion.py
│   │   │   └── analytics.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── logging.py
│   │   │   ├── validators.py
│   │   │   └── helpers.py
│   │   └── migrations/
│   │       ├── env.py
│   │       └── versions/
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── unit/
│   │   │   ├── test_extractors.py
│   │   │   ├── test_converters.py
│   │   │   └── test_services.py
│   │   ├── integration/
│   │   │   ├── test_api.py
│   │   │   └── test_database.py
│   │   └── fixtures/
│   │       ├── sample_news.html
│   │       └── test_data.json
│   ├── scripts/
│   │   ├── start.sh
│   │   ├── migration.sh
│   │   └── test.sh
│   ├── requirements/
│   │   ├── base.txt
│   │   ├── dev.txt
│   │   └── prod.txt
│   ├── Dockerfile
│   ├── pyproject.toml
│   └── README.md
├── 🎨 frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── globals.css
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── register/
│   │   │   │       └── page.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── page.tsx
│   │   │   │   └── analytics/
│   │   │   │       └── page.tsx
│   │   │   └── api/
│   │   │       └── proxy/
│   │   │           └── route.ts
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   └── toast.tsx
│   │   │   ├── layout/
│   │   │   │   ├── header.tsx
│   │   │   │   ├── sidebar.tsx
│   │   │   │   └── footer.tsx
│   │   │   ├── converter/
│   │   │   │   ├── url-input.tsx
│   │   │   │   ├── platform-selector.tsx
│   │   │   │   ├── conversion-result.tsx
│   │   │   │   └── conversion-history.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login-form.tsx
│   │   │   │   └── register-form.tsx
│   │   │   └── analytics/
│   │   │       ├── usage-chart.tsx
│   │   │       └── stats-card.tsx
│   │   ├── lib/
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── utils.ts
│   │   │   └── validators.ts
│   │   ├── hooks/
│   │   │   ├── use-auth.ts
│   │   │   ├── use-converter.ts
│   │   │   └── use-analytics.ts
│   │   ├── store/
│   │   │   ├── auth-store.ts
│   │   │   ├── converter-store.ts
│   │   │   └── analytics-store.ts
│   │   ├── types/
│   │   │   ├── auth.ts
│   │   │   ├── converter.ts
│   │   │   └── analytics.ts
│   │   └── styles/
│   │       ├── globals.css
│   │       └── components.css
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── images/
│   ├── tests/
│   │   ├── __tests__/
│   │   │   ├── components/
│   │   │   └── pages/
│   │   └── e2e/
│   │       └── converter.spec.ts
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   ├── package.json
│   ├── Dockerfile
│   └── README.md
├── 📊 monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml
│   │   └── alerts.yml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── app-metrics.json
│   │   │   └── system-metrics.json
│   │   └── provisioning/
│   │       ├── dashboards/
│   │       └── datasources/
│   └── loki/
│       └── loki.yml
├── 🧪 tests/
│   ├── performance/
│   │   ├── load-test.js
│   │   └── stress-test.js
│   ├── security/
│   │   ├── auth-test.py
│   │   └── injection-test.py
│   └── e2e/
│       ├── user-journey.spec.ts
│       └── conversion-flow.spec.ts
├── 📋 docs/
│   ├── api/
│   │   ├── README.md
│   │   └── openapi.json
│   ├── deployment/
│   │   ├── production.md
│   │   └── development.md
│   ├── architecture/
│   │   ├── system-design.md
│   │   └── database-schema.md
│   └── user-guides/
│       ├── getting-started.md
│       └── api-usage.md
├── 🔧 scripts/
│   ├── setup.sh
│   ├── deploy.sh
│   ├── backup.sh
│   └── health-check.sh
├── 🌍 k8s/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── backend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── frontend/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── database/
│   │   ├── postgres.yaml
│   │   └── redis.yaml
│   └── ingress/
│       └── traefik.yaml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       └── security.yml
├── .env.template
├── .gitignore
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## 🏗️ 아키텍처 설계 원칙

### 1. 관심사의 분리 (Separation of Concerns)
```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                      │
│              (Next.js Frontend)                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              │
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                            │
│                  (Nginx + Traefik)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Load Balancing
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                        │
│                  (FastAPI Backend)                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Auth API   │  │ Convert API │  │Analytics API│        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Data Access
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Data Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ PostgreSQL  │  │    Redis    │  │  File Store │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 2. 마이크로서비스 분리 전략
```yaml
Services:
  Auth Service:
    - 사용자 인증/인가
    - JWT 토큰 관리
    - 사용자 프로필 관리
    
  Converter Service:
    - 뉴스 추출 (Web Scraping)
    - AI 변환 (OpenAI/Anthropic)
    - 결과 캐싱
    
  Analytics Service:
    - 사용량 추적
    - 사용자 행동 분석
    - 성능 메트릭
    
  Notification Service:
    - 이메일 알림
    - 푸시 알림
    - 사용량 알림
```

### 3. 데이터 모델 설계
```python
# models/base.py
from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

# models/user.py
from sqlalchemy import Column, String, Boolean, Integer
from .base import BaseModel

class User(BaseModel):
    __tablename__ = "users"
    
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    daily_usage = Column(Integer, default=0)
    
# models/conversion.py
from sqlalchemy import Column, String, Text, JSON, ForeignKey
from .base import BaseModel

class Conversion(BaseModel):
    __tablename__ = "conversions"
    
    user_id = Column(Integer, ForeignKey("users.id"))
    source_url = Column(String)
    platform = Column(String)  # twitter, threads, linkedin
    original_content = Column(Text)
    converted_content = Column(Text)
    metadata = Column(JSON)
    processing_time = Column(Integer)  # milliseconds
```

### 4. 보안 아키텍처
```yaml
Security Layers:
  1. Network Security:
     - Nginx SSL/TLS termination
     - Rate limiting
     - DDoS protection
     
  2. Application Security:
     - JWT authentication
     - Input validation
     - SQL injection prevention
     - XSS protection
     
  3. Data Security:
     - Database encryption at rest
     - Redis password protection
     - Sensitive data masking
     
  4. Infrastructure Security:
     - Container security scanning
     - Secrets management
     - Access control
```

### 5. 성능 최적화 전략
```yaml
Performance Optimizations:
  1. Caching Strategy:
     - Redis for API responses
     - Browser caching for static assets
     - CDN for global distribution
     
  2. Database Optimization:
     - Connection pooling
     - Query optimization
     - Indexing strategy
     
  3. Application Optimization:
     - Async/await everywhere
     - Background task processing
     - Response compression
     
  4. Frontend Optimization:
     - Code splitting
     - Image optimization
     - Server-side rendering
```

## 📊 모니터링 및 관찰성

### 1. 메트릭 수집
```yaml
Application Metrics:
  - Request/response times
  - Error rates
  - Throughput
  - User activity
  
Business Metrics:
  - Conversion rates
  - User retention
  - Revenue metrics
  - Feature usage
  
Infrastructure Metrics:
  - CPU/Memory usage
  - Database performance
  - Network latency
  - Disk I/O
```

### 2. 로깅 전략
```python
# utils/logging.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        
    def log_event(self, level: str, message: str, **kwargs):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level,
            "message": message,
            "service": "newsforge-api",
            **kwargs
        }
        
        if level == "ERROR":
            self.logger.error(json.dumps(log_entry))
        elif level == "WARNING":
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))
```

## 🔄 CI/CD 파이프라인

### 1. GitHub Actions 워크플로우
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements/dev.txt
      - name: Run tests
        run: |
          pytest tests/ --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run security scan
        uses: pypa/gh-action-pip-audit@v1.0.8
        
  deploy:
    needs: [test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          ./scripts/deploy.sh
```

이 구조는 확장 가능하고 유지보수 가능한 프로덕션 시스템을 위한 기반을 제공합니다. 