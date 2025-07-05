# 📁 NewsForge Pro - 최적화된 프로젝트 구조

## 🏗️ 루트 디렉토리 구조

```
newsforge-pro/
├── 📦 backend/                 # FastAPI 백엔드 서비스
│   ├── services/
│   │   ├── gateway/           # API Gateway
│   │   ├── converter/         # 핵심 변환 서비스
│   │   ├── user/             # 사용자 관리
│   │   ├── payment/          # 결제 처리
│   │   └── analytics/        # 분석 서비스
│   ├── shared/               # 공통 모듈
│   ├── tests/               # 백엔드 테스트
│   ├── docker-compose.yml   # 로컬 개발 환경
│   └── requirements.txt     # Python 의존성
├── 🌐 frontend/              # WordPress + React 프론트엔드
│   ├── wordpress-theme/     # 커스텀 WordPress 테마
│   ├── react-components/    # React 컴포넌트
│   ├── assets/             # 정적 자산
│   └── build/              # 빌드 결과물
├── 🚀 infrastructure/        # 인프라 코드
│   ├── kubernetes/          # K8s 매니페스트
│   ├── helm-charts/         # Helm 차트
│   ├── terraform/           # 인프라 코드
│   └── monitoring/          # 모니터링 설정
├── 📊 docs/                  # 문서화
│   ├── api/                 # API 문서
│   ├── deployment/          # 배포 가이드
│   └── business/            # 비즈니스 문서
├── 🧪 scripts/               # 운영 스크립트
│   ├── deploy.sh            # 배포 스크립트
│   ├── backup.sh            # 백업 스크립트
│   └── migration.py         # 데이터 마이그레이션
└── 📋 .github/               # GitHub Actions
    └── workflows/           # CI/CD 파이프라인
```

## 🔧 백엔드 서비스 상세 구조

### **1. API Gateway (services/gateway/)**

```
gateway/
├── main.py                  # FastAPI 앱 진입점
├── middleware/
│   ├── __init__.py
│   ├── auth.py             # JWT 인증
│   ├── rate_limit.py       # 속도 제한
│   ├── cors.py             # CORS 설정
│   └── logging.py          # 로깅 미들웨어
├── routers/
│   ├── __init__.py
│   ├── health.py           # 헬스체크
│   ├── auth.py             # 인증 라우터
│   └── proxy.py            # 서비스 프록시
├── models/
│   ├── __init__.py
│   ├── request.py          # 요청 모델
│   └── response.py         # 응답 모델
├── config/
│   ├── __init__.py
│   ├── settings.py         # 설정 관리
│   └── database.py         # DB 연결
└── utils/
    ├── __init__.py
    ├── security.py         # 보안 유틸
    └── helpers.py          # 도우미 함수
```

### **2. 변환 서비스 (services/converter/)**

```
converter/
├── main.py                 # 변환 서비스 메인
├── api/
│   ├── __init__.py
│   ├── endpoints.py        # API 엔드포인트
│   └── websocket.py        # 실시간 처리 상태
├── core/
│   ├── __init__.py
│   ├── extractor.py        # 뉴스 추출 엔진
│   ├── converter.py        # AI 변환 엔진
│   └── validator.py        # 결과 검증
├── extractors/
│   ├── __init__.py
│   ├── base.py             # 추출기 베이스
│   ├── selenium_extractor.py
│   ├── requests_extractor.py
│   └── newspaper_extractor.py
├── converters/
│   ├── __init__.py
│   ├── base.py             # 변환기 베이스
│   ├── openai_converter.py
│   ├── anthropic_converter.py
│   └── local_converter.py
├── workers/
│   ├── __init__.py
│   ├── celery_app.py       # Celery 설정
│   ├── conversion_worker.py
│   └── cleanup_worker.py
├── models/
│   ├── __init__.py
│   ├── conversion.py       # 변환 모델
│   └── result.py           # 결과 모델
└── tests/
    ├── __init__.py
    ├── test_extractors.py
    └── test_converters.py
```

### **3. 사용자 서비스 (services/user/)**

```
user/
├── main.py                 # 사용자 서비스 메인
├── api/
│   ├── __init__.py
│   ├── auth.py            # 인증 API
│   ├── profile.py         # 프로필 관리
│   └── subscription.py    # 구독 관리
├── models/
│   ├── __init__.py
│   ├── user.py           # 사용자 모델
│   ├── subscription.py   # 구독 모델
│   └── usage.py          # 사용량 모델
├── services/
│   ├── __init__.py
│   ├── auth_service.py   # 인증 서비스
│   ├── user_service.py   # 사용자 서비스
│   └── usage_tracker.py  # 사용량 추적
└── db/
    ├── __init__.py
    ├── connection.py     # DB 연결
    └── migrations/       # DB 마이그레이션
```

## 🌐 프론트엔드 구조

### **WordPress 테마 (frontend/wordpress-theme/)**

```
wordpress-theme/
├── style.css              # 테마 정보
├── functions.php          # WordPress 훅 & 기능
├── index.php              # 메인 템플릿
├── header.php             # 헤더 (AdSense 최적화)
├── footer.php             # 푸터 (수익화 요소)
├── page-converter.php     # 변환 페이지 템플릿
├── page-pricing.php       # 요금제 페이지
├── page-dashboard.php     # 사용자 대시보드
├── single.php             # 블로그 포스트
├── inc/
│   ├── theme-setup.php    # 테마 설정
│   ├── adsense.php        # AdSense 통합
│   ├── analytics.php      # Google Analytics
│   ├── security.php       # 보안 설정
│   └── performance.php    # 성능 최적화
├── templates/
│   ├── parts/
│   │   ├── navigation.php
│   │   ├── sidebar.php
│   │   └── footer-widgets.php
│   └── pages/
│       ├── home.php
│       ├── about.php
│       └── contact.php
├── assets/
│   ├── css/
│   │   ├── main.css       # 메인 스타일
│   │   ├── responsive.css # 반응형 스타일
│   │   └── adsense.css    # 광고 최적화
│   ├── js/
│   │   ├── main.js        # 메인 JavaScript
│   │   ├── converter.js   # 변환기 앱
│   │   └── analytics.js   # 분석 추적
│   └── images/
│       ├── logo.svg
│       ├── hero-bg.jpg
│       └── icons/
└── languages/             # 다국어 지원
    ├── ko_KR.po
    └── en_US.po
```

### **React 컴포넌트 (frontend/react-components/)**

```
react-components/
├── src/
│   ├── components/
│   │   ├── converter/
│   │   │   ├── ConverterForm.tsx
│   │   │   ├── ResultDisplay.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   └── ShareButton.tsx
│   │   ├── auth/
│   │   │   ├── LoginForm.tsx
│   │   │   ├── RegisterForm.tsx
│   │   │   └── PasswordReset.tsx
│   │   ├── dashboard/
│   │   │   ├── UsageStats.tsx
│   │   │   ├── ConversionHistory.tsx
│   │   │   └── SubscriptionInfo.tsx
│   │   ├── payment/
│   │   │   ├── PricingCards.tsx
│   │   │   ├── CheckoutForm.tsx
│   │   │   └── PaymentSuccess.tsx
│   │   └── common/
│   │       ├── Header.tsx
│   │       ├── Footer.tsx
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorBoundary.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useConverter.ts
│   │   ├── useSubscription.ts
│   │   └── useAnalytics.ts
│   ├── services/
│   │   ├── api.ts         # API 클라이언트
│   │   ├── auth.ts        # 인증 서비스
│   │   └── analytics.ts   # 분석 서비스
│   ├── utils/
│   │   ├── helpers.ts
│   │   ├── constants.ts
│   │   └── types.ts
│   └── styles/
│       ├── globals.css
│       ├── components.css
│       └── utilities.css
├── public/
│   ├── favicon.ico
│   └── manifest.json
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── webpack.config.js
```

## 🚀 인프라 코드

### **Kubernetes 매니페스트 (infrastructure/kubernetes/)**

```
kubernetes/
├── namespaces/
│   ├── newsforge-prod.yaml
│   └── newsforge-staging.yaml
├── services/
│   ├── gateway/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   ├── converter/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml       # Horizontal Pod Autoscaler
│   ├── user/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── payment/
│       ├── deployment.yaml
│       └── service.yaml
├── databases/
│   ├── postgresql/
│   │   ├── statefulset.yaml
│   │   ├── service.yaml
│   │   └── pvc.yaml
│   └── redis/
│       ├── deployment.yaml
│       └── service.yaml
├── monitoring/
│   ├── prometheus/
│   │   ├── deployment.yaml
│   │   ├── configmap.yaml
│   │   └── service.yaml
│   └── grafana/
│       ├── deployment.yaml
│       └── dashboards/
└── secrets/
    ├── api-keys.yaml
    ├── database-credentials.yaml
    └── ssl-certificates.yaml
```

## 📊 모니터링 & 로깅

### **Prometheus 설정 (infrastructure/monitoring/)**

```
monitoring/
├── prometheus/
│   ├── prometheus.yml     # Prometheus 설정
│   ├── alerts/
│   │   ├── service-alerts.yml
│   │   ├── business-alerts.yml
│   │   └── infrastructure-alerts.yml
│   └── rules/
│       ├── recording-rules.yml
│       └── alerting-rules.yml
├── grafana/
│   ├── dashboards/
│   │   ├── business-metrics.json
│   │   ├── technical-metrics.json
│   │   ├── user-analytics.json
│   │   └── revenue-tracking.json
│   └── provisioning/
│       ├── datasources.yml
│       └── dashboards.yml
├── elasticsearch/
│   ├── index-templates/
│   │   ├── application-logs.json
│   │   └── access-logs.json
│   └── kibana/
│       ├── saved-objects.json
│       └── index-patterns.json
└── alertmanager/
    ├── alertmanager.yml
    └── templates/
        ├── slack-template.tmpl
        └── email-template.tmpl
```

## 🧪 테스트 구조

### **통합 테스트 (tests/)**

```
tests/
├── unit/                  # 단위 테스트
│   ├── backend/
│   │   ├── test_converter.py
│   │   ├── test_extractor.py
│   │   └── test_auth.py
│   └── frontend/
│       ├── converter.test.tsx
│       ├── auth.test.tsx
│       └── dashboard.test.tsx
├── integration/           # 통합 테스트
│   ├── test_api_flow.py
│   ├── test_payment_flow.py
│   └── test_user_journey.py
├── e2e/                   # E2E 테스트
│   ├── cypress/
│   │   ├── integration/
│   │   │   ├── conversion-flow.spec.js
│   │   │   ├── payment-flow.spec.js
│   │   │   └── user-registration.spec.js
│   │   └── support/
│   └── playwright/
│       ├── tests/
│       └── config/
├── performance/           # 성능 테스트
│   ├── load-tests/
│   │   ├── conversion-load.js
│   │   └── api-load.js
│   └── stress-tests/
├── security/              # 보안 테스트
│   ├── penetration/
│   └── vulnerability/
└── fixtures/              # 테스트 데이터
    ├── sample-articles.json
    └── mock-responses.json
```

## 📋 핵심 설정 파일들

### **환경 설정**

```bash
# .env.production
DATABASE_URL=postgresql://user:pass@db:5432/newsforge
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
JWT_SECRET=your-jwt-secret
STRIPE_SECRET_KEY=sk_live_...
GOOGLE_ANALYTICS_ID=GA_MEASUREMENT_ID
ADSENSE_CLIENT_ID=ca-pub-...
SENTRY_DSN=https://...@sentry.io/...
```

### **Docker Compose (개발환경)**

```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  gateway:
    build: ./backend/services/gateway
    ports:
      - "8000:8000"
    environment:
      - ENV=development
    volumes:
      - ./backend/services/gateway:/app
    depends_on:
      - postgresql
      - redis

  converter:
    build: ./backend/services/converter
    ports:
      - "8001:8001"
    environment:
      - ENV=development
    volumes:
      - ./backend/services/converter:/app
    depends_on:
      - postgresql
      - redis

  postgresql:
    image: postgres:15
    environment:
      POSTGRES_DB: newsforge
      POSTGRES_USER: developer
      POSTGRES_PASSWORD: dev_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  wordpress:
    image: wordpress:latest
    ports:
      - "3000:80"
    environment:
      WORDPRESS_DB_HOST: postgresql
      WORDPRESS_DB_USER: developer
      WORDPRESS_DB_PASSWORD: dev_password
      WORDPRESS_DB_NAME: wordpress
    volumes:
      - ./frontend/wordpress-theme:/var/www/html/wp-content/themes/newsforge
      - wordpress_data:/var/www/html

volumes:
  postgres_data:
  wordpress_data:
```

이 구조는 확장성, 유지보수성, 그리고 상용화 요구사항을 모두 고려하여 설계되었습니다. 각 컴포넌트는 독립적으로 개발, 테스트, 배포할 수 있으며, 마이크로서비스 아키텍처를 통해 높은 가용성과 확장성을 보장합니다. 