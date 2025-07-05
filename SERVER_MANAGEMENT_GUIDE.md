# 🔧 NewsForge Pro 서버 관리 가이드

## 📋 해결된 서버 연결 문제들

### 🔍 근본적인 원인들
1. **서버 시작 위치 문제**: PYTHONPATH 설정 오류
2. **포트 충돌**: 기존 프로세스가 완전히 종료되지 않음
3. **Health Check 타임아웃**: 5초는 너무 짧음
4. **무한 재시작**: 파일 변경 감지로 인한 지속적 재시작
5. **서버 상태 모니터링 부족**: 준비 상태 확인 메커니즘 없음

### ✅ 적용된 해결책
1. **통합 서버 관리 스크립트** (`run_server.py`)
2. **자동 포트 정리 기능**
3. **향상된 Health Check** (10초 타임아웃, 3회 재시도)
4. **자동 서버 복구 메커니즘**
5. **체계적인 로깅 및 모니터링**

## 🚀 빠른 시작

### 1. 서버 시작
```bash
# 방법 1: 통합 관리 스크립트 사용 (권장)
./manage.sh start-api

# 방법 2: 직접 실행
cd newsforge-pro/backend
python run_server.py start
```

### 2. 서버 상태 확인
```bash
# Health check
./manage.sh health-api

# 상세 상태 확인
./manage.sh status-api
```

### 3. 서버 중지
```bash
./manage.sh stop-api
```

### 4. 전체 서버 시작 (API + Web)
```bash
./manage.sh full-start
```

## 📖 명령어 가이드

### 🎛️ 통합 관리 스크립트 (`./manage.sh`)

```bash
# FastAPI 서버 관리
./manage.sh start-api          # API 서버 시작
./manage.sh stop-api           # API 서버 중지
./manage.sh restart-api        # API 서버 재시작
./manage.sh status-api         # API 서버 상태 확인
./manage.sh health-api         # Health Check 수행

# Next.js 웹 서버
./manage.sh start-web          # 웹 서버 시작

# 전체 관리
./manage.sh full-start         # 전체 서버 시작
./manage.sh full-stop          # 전체 서버 중지
./manage.sh install-deps       # 의존성 설치

# 프로덕션 모드
./manage.sh start-api --production
```

### 🔧 서버 관리 스크립트 (`run_server.py`)

```bash
cd newsforge-pro/backend

# 기본 명령어
python run_server.py start     # 서버 시작
python run_server.py stop      # 서버 중지
python run_server.py restart   # 서버 재시작
python run_server.py status    # 상태 확인
python run_server.py health    # Health Check

# 프로덕션 모드
python run_server.py start --production
```

## 🛠️ 문제 해결

### ❌ 서버 연결 실패 시

1. **포트 충돌 해결**
   ```bash
   # 포트 8000 사용 프로세스 확인
   lsof -i :8000
   
   # 강제 종료
   kill -9 <PID>
   
   # 또는 자동 정리 사용
   ./manage.sh restart-api
   ```

2. **서버 시작 실패 시**
   ```bash
   # 의존성 재설치
   ./manage.sh install-deps
   
   # 서버 강제 재시작
   ./manage.sh stop-api
   sleep 5
   ./manage.sh start-api
   ```

3. **Health Check 실패 시**
   ```bash
   # 서버 상태 확인
   ./manage.sh status-api
   
   # 로그 확인 (서버가 실행 중인 터미널에서)
   # 서버 재시작
   ./manage.sh restart-api
   ```

### 🔍 디버깅 팁

1. **서버 로그 확인**
   - 서버를 포그라운드로 실행하여 실시간 로그 확인
   - 에러 메시지와 스택 트레이스 분석

2. **Health Check URL 직접 접속**
   ```bash
   curl http://127.0.0.1:8000/api/v1/health
   ```

3. **API 문서 확인**
   - 브라우저에서 `http://127.0.0.1:8000/docs` 접속

## 🔄 자동 복구 기능

### 🤖 Next.js API에서의 자동 복구
- **3단계 Health Check**: 최대 3회 재시도
- **자동 서버 시작**: 연결 실패 시 서버 자동 시작 시도
- **폴백 메커니즘**: FastAPI 실패 시 Python 변환기로 자동 전환

### 📊 향상된 폴링 시스템
- **90초 타임아웃**: 충분한 처리 시간 확보
- **점진적 재시도**: 에러 발생 시 대기 시간 점진 증가
- **연속 에러 방지**: 5회 연속 실패 시 자동 중단

## 📈 모니터링 및 성능

### 🎯 서버 성능 지표
- **시작 시간**: 평균 2-5초
- **Health Check**: 응답 시간 < 1초
- **변환 처리**: 평균 15-30초

### 📋 로그 레벨
- **INFO**: 일반적인 서버 동작
- **ERROR**: 변환 실패 및 시스템 오류
- **DEBUG**: 상세한 디버깅 정보

## 🚨 응급 상황 대응

### 🔥 서버 완전 멈춤 시
```bash
# 모든 관련 프로세스 종료
pkill -f "uvicorn"
pkill -f "python.*main.py"

# 포트 강제 정리
lsof -ti:8000 | xargs kill -9

# 서버 재시작
./manage.sh start-api
```

### 💥 API 응답 없음 시
```bash
# 서버 프로세스 확인
ps aux | grep uvicorn

# 네트워크 연결 확인
netstat -an | grep 8000

# 서버 강제 재시작
./manage.sh restart-api
```

## 📞 지원 및 문의

### 🔗 유용한 링크
- **FastAPI 문서**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/api/v1/health
- **Next.js 앱**: http://localhost:3000

### 🐛 버그 리포트
서버 관련 문제 발생 시 다음 정보를 포함해 주세요:
1. 사용한 명령어
2. 에러 메시지 전문
3. 서버 로그
4. 시스템 환경 (OS, Python 버전 등)

---

이제 서버 연결 문제는 과거의 일입니다! 🎉 