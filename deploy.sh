#!/bin/bash

# 뉴스 변환 서비스 배포 스크립트
# 개발/프로덕션 환경에서 사용

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 로그 함수
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# 사용법
usage() {
    echo "사용법: $0 [dev|prod|stop|restart|logs]"
    echo ""
    echo "옵션:"
    echo "  dev     - 개발 환경으로 시작"
    echo "  prod    - 프로덕션 환경으로 시작"
    echo "  stop    - 모든 서비스 중지"
    echo "  restart - 서비스 재시작"
    echo "  logs    - 로그 확인"
    echo "  health  - 서비스 상태 확인"
    exit 1
}

# 환경 변수 확인
check_env() {
    log "환경 변수 확인 중..."
    
    if [[ ! -f .env ]]; then
        warn ".env 파일이 없습니다. .env.example을 참고하여 생성하세요."
        
        # .env.example 생성
        cat > .env << EOF
# 데이터베이스 설정
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/news_to_social

# NextAuth.js 설정
NEXTAUTH_SECRET=your-secret-key-here
NEXTAUTH_URL=http://localhost:3000

# Google OAuth 설정
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret

# API 키 암호화
ENCRYPTION_SECRET=your-32-character-encryption-key

# Python FastAPI 서버 설정
PYTHON_API_URL=http://localhost:8000

# 선택사항: 시스템 기본 API 키
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key

# Google AdSense
GOOGLE_ADSENSE_ID=your-adsense-id

# 프로덕션 환경 설정
NODE_ENV=development
VERCEL_ENV=development
EOF
        
        error ".env 파일을 생성했습니다. 값을 설정한 후 다시 실행하세요."
    fi
    
    source .env
    log "환경 변수 로드 완료"
}

# Docker 확인
check_docker() {
    log "Docker 확인 중..."
    
    if ! command -v docker &> /dev/null; then
        error "Docker가 설치되어 있지 않습니다."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose가 설치되어 있지 않습니다."
    fi
    
    log "Docker 확인 완료"
}

# 의존성 설치
install_dependencies() {
    log "의존성 설치 중..."
    
    # Python 의존성
    if [[ -f requirements.txt ]]; then
        log "Python 의존성 설치 중..."
        pip install -r requirements.txt || warn "Python 의존성 설치 실패"
    fi
    
    # Node.js 의존성
    if [[ -f news-to-social-web/package.json ]]; then
        log "Node.js 의존성 설치 중..."
        cd news-to-social-web
        npm install || warn "Node.js 의존성 설치 실패"
        cd ..
    fi
    
    log "의존성 설치 완료"
}

# 데이터베이스 마이그레이션
migrate_database() {
    log "데이터베이스 마이그레이션 중..."
    
    cd news-to-social-web
    
    # Prisma 마이그레이션
    if [[ -f prisma/schema.prisma ]]; then
        npx prisma migrate deploy || warn "마이그레이션 실패"
        npx prisma generate || warn "Prisma 생성 실패"
    fi
    
    cd ..
    log "데이터베이스 마이그레이션 완료"
}

# 개발 환경 시작
start_dev() {
    log "개발 환경 시작 중..."
    
    # 기존 컨테이너 정리
    docker-compose down || true
    
    # 개발 환경 시작
    docker-compose up -d postgres redis
    
    # 데이터베이스 준비 대기
    sleep 5
    
    # 마이그레이션 실행
    migrate_database
    
    log "개발 환경 준비 완료"
    log "다음 명령어로 서비스를 시작하세요:"
    log "  터미널 1: python news_converter_api.py --reload"
    log "  터미널 2: cd news-to-social-web && npm run dev"
}

# 프로덕션 환경 시작
start_prod() {
    log "프로덕션 환경 시작 중..."
    
    # 기존 컨테이너 정리
    docker-compose down || true
    
    # 이미지 빌드
    docker-compose build
    
    # 프로덕션 환경 시작
    docker-compose up -d
    
    # 서비스 준비 대기
    sleep 10
    
    # 건강 상태 확인
    health_check
    
    log "프로덕션 환경 시작 완료"
}

# 서비스 중지
stop_services() {
    log "서비스 중지 중..."
    docker-compose down
    log "서비스 중지 완료"
}

# 서비스 재시작
restart_services() {
    log "서비스 재시작 중..."
    docker-compose restart
    log "서비스 재시작 완료"
}

# 로그 확인
show_logs() {
    log "로그 확인 중..."
    docker-compose logs -f --tail=100
}

# 건강 상태 확인
health_check() {
    log "서비스 상태 확인 중..."
    
    # Next.js 서비스 확인
    if curl -f http://localhost:3000/health > /dev/null 2>&1; then
        log "✅ Next.js 서비스 정상"
    else
        warn "❌ Next.js 서비스 비정상"
    fi
    
    # Python API 서비스 확인
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Python API 서비스 정상"
    else
        warn "❌ Python API 서비스 비정상"
    fi
    
    # 데이터베이스 확인
    if docker-compose exec postgres pg_isready > /dev/null 2>&1; then
        log "✅ PostgreSQL 데이터베이스 정상"
    else
        warn "❌ PostgreSQL 데이터베이스 비정상"
    fi
    
    log "상태 확인 완료"
}

# 메인 로직
main() {
    case "${1:-}" in
        dev)
            check_env
            check_docker
            install_dependencies
            start_dev
            ;;
        prod)
            check_env
            check_docker
            start_prod
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        logs)
            show_logs
            ;;
        health)
            health_check
            ;;
        *)
            usage
            ;;
    esac
}

# 스크립트 실행
main "$@" 