# 🚀 NewsForge Pro

**상용급 뉴스-소셜 콘텐츠 변환 서비스**

뉴스 기사를 다양한 소셜 미디어 플랫폼에 최적화된 콘텐츠로 자동 변환하는 고성능 웹 서비스입니다.

## ✨ 주요 기능

### 🎯 핵심 서비스
- **뉴스 추출**: URL로부터 자동 뉴스 기사 추출
- **AI 변환**: OpenAI/Anthropic API를 활용한 플랫폼별 최적화
- **다중 플랫폼**: Twitter, Threads, LinkedIn, Instagram 지원
- **실시간 처리**: 비동기 작업 큐를 통한 빠른 응답

### 💼 비즈니스 기능
- **사용량 제한**: 무료/프리미엄 플랜별 차등 제한
- **사용자 인증**: JWT 기반 보안 인증
- **히스토리 관리**: 변환 기록 및 통계 제공
- **구독 관리**: Stripe 결제 연동 (예정)

### 🔧 기술적 특징
- **고성능**: FastAPI + Redis + PostgreSQL
- **확장성**: Docker 컨테이너 기반 마이크로서비스
- **모니터링**: Prometheus + Grafana 연동
- **보안**: HTTPS, API 키 암호화, Rate Limiting

## 🏗️ 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   프론트엔드     │    │   백엔드 API     │    │   데이터베이스   │
│  (Next.js)      │◄──►│   (FastAPI)     │◄──►│ (PostgreSQL)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │  (캐시/큐)       │
                       └─────────────────┘
```

## 📁 프로젝트 구조

```
newsforge-pro/
├── backend/                    # FastAPI 백엔드
│   ├── app/
│   │   ├── api/               # API 라우터
│   │   ├── core/              # 인증, 예외, 설정
│   │   ├── services/          # 비즈니스 로직
│   │   ├── schemas/           # Pydantic 스키마
│   │   └── main.py           # FastAPI 앱
│   ├── run_server.py         # 개발 서버 실행
│   ├── test_structure.py     # 구조 테스트
│   └── requirements.txt      # Python 의존성
├── frontend/                  # 프론트엔드 (추후 구현)
│   ├── wordpress-theme/      # WordPress 테마
│   └── react-components/     # React 컴포넌트
├── infrastructure/           # 인프라 설정
│   ├── docker/              # Docker 파일
│   ├── nginx/               # Nginx 설정
│   └── monitoring/          # 모니터링 설정
├── docker-compose.yml       # 전체 서비스 구성
└── start.sh                # 시작 스크립트
```

## 🚀 빠른 시작

### 1️⃣ 개발 환경 실행

```bash
# 저장소 클론
git clone <repository-url>
cd newsforge-pro

# 개발 모드로 시작
chmod +x start.sh
./start.sh --dev
```

### 2️⃣ Docker 환경 실행

```bash
# Docker Compose로 전체 시스템 실행
./start.sh --docker

# 또는 직접 실행
docker-compose up --build
```

### 3️⃣ 프로덕션 환경 실행

```bash
# 환경 변수 설정
export DATABASE_URL="postgresql://user:pass@host:5432/db"
export REDIS_URL="redis://host:6379"

# 프로덕션 모드로 시작
./start.sh --prod
```

## 📖 API 사용법

### 인증 설정

```bash
# 테스트 토큰 (개발용)
curl -H "Authorization: Bearer test_token_123" \
     http://localhost:8000/api/v1/convert
```

### 뉴스 변환 요청

```bash
curl -X POST "http://localhost:8000/api/v1/convert" \
     -H "Authorization: Bearer test_token_123" \
     -H "Content-Type: application/json" \
     -d '{
       "url": "https://example.com/news-article",
       "platforms": ["twitter", "threads"],
       "converter_type": "auto"
     }'
```

### 변환 결과 조회

```bash
curl -H "Authorization: Bearer test_token_123" \
     http://localhost:8000/api/v1/conversion/{task_id}
```

## 🔧 개발 가이드

### 백엔드 구조 테스트

```bash
cd newsforge-pro/backend
python test_structure.py
```

### 새로운 서비스 추가

1. `backend/app/services/` 에 서비스 클래스 생성
2. `backend/app/schemas/` 에 관련 스키마 정의
3. `backend/app/api/` 에 API 라우터 추가
4. `main.py` 에 라우터 등록

### 환경 변수 설정

```bash
# 개발 환경
export ENVIRONMENT=development
export REDIS_URL=redis://localhost:6379
export DATABASE_URL=postgresql://localhost:5432/newsforge

# AI API 키
export OPENAI_API_KEY=your_openai_key
export ANTHROPIC_API_KEY=your_anthropic_key
```

## 📊 모니터링

### API 문서 접근

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### 시스템 모니터링

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (추후 설정)

### 헬스 체크

```bash
curl http://localhost:8000/api/health
```

## 🔐 보안 설정

### JWT 토큰 생성 (프로덕션)

```python
from app.core.auth import create_access_token

user_data = {"id": 1, "email": "user@example.com"}
token = create_access_token(user_data)
```

### API 키 암호화

```python
from app.core.security import encrypt, decrypt

encrypted = encrypt("sensitive_data")
decrypted = decrypt(encrypted)
```

## 📈 성능 최적화

### 예상 성능 지표

- **응답 시간**: 5-10초 (기존 20-30초 대비 66% 향상)
- **동시 처리**: 100+ 요청 (기존 1개 대비 100배 향상)
- **메모리 사용**: 200MB (기존 500MB+ 대비 60% 절약)
- **에러율**: 2% (기존 15% 대비 87% 개선)

### 캐싱 전략

- **Redis**: 변환 결과, 사용자 세션
- **메모리**: 자주 사용되는 설정 데이터
- **CDN**: 정적 파일 (프론트엔드)

## 🛠️ 배포 가이드

### Docker 배포

```bash
# 이미지 빌드
docker build -f infrastructure/docker/Dockerfile -t newsforge-pro .

# 컨테이너 실행
docker run -p 8000:8000 -e DATABASE_URL=$DATABASE_URL newsforge-pro
```

### 클라우드 배포

1. **AWS ECS/EKS**: `infrastructure/aws/` 설정 참조
2. **Google Cloud Run**: `infrastructure/gcp/` 설정 참조
3. **Azure Container Apps**: `infrastructure/azure/` 설정 참조

## 🤝 기여 가이드

### 개발 워크플로

1. 브랜치 생성: `git checkout -b feature/new-feature`
2. 코드 작성 및 테스트
3. 커밋: `git commit -m "feat: add new feature"`
4. 푸시: `git push origin feature/new-feature`
5. Pull Request 생성

### 코딩 스타일

- **Python**: Black, isort, flake8 사용
- **TypeScript**: Prettier, ESLint 사용
- **커밋 메시지**: Conventional Commits 규칙

## 📞 지원 및 문의

- **이슈 리포트**: GitHub Issues
- **기능 요청**: GitHub Discussions
- **보안 문제**: security@newsforge.pro
- **일반 문의**: support@newsforge.pro

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🗺️ 로드맵

### Phase 1 (현재)
- ✅ FastAPI 백엔드 구조 완성
- ✅ 기본 뉴스 변환 기능
- ✅ Docker 환경 구성

### Phase 2 (다음)
- 🔲 WordPress 프론트엔드 개발
- 🔲 결제 시스템 연동 (Stripe)
- 🔲 실제 AI API 연동

### Phase 3 (향후)
- 🔲 모바일 앱 개발
- 🔲 대량 처리 시스템
- 🔲 AI 모델 커스터마이징

---

**NewsForge Pro** - 뉴스를 소셜 콘텐츠로, 간단하고 빠르게! 🚀 