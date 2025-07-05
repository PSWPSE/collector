#!/bin/bash

# NewsForge Pro 통합 관리 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/newsforge-pro/backend"
FRONTEND_DIR="$SCRIPT_DIR/news-to-social-web"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_help() {
    echo -e "${BLUE}NewsForge Pro 관리 스크립트${NC}"
    echo ""
    echo "사용법: $0 <command> [options]"
    echo ""
    echo "Commands:"
    echo "  start-api      FastAPI 서버 시작"
    echo "  stop-api       FastAPI 서버 중지"
    echo "  restart-api    FastAPI 서버 재시작"
    echo "  status-api     FastAPI 서버 상태 확인"
    echo "  health-api     FastAPI 서버 Health Check"
    echo ""
    echo "  start-web      Next.js 웹 애플리케이션 시작"
    echo "  install-deps   의존성 설치"
    echo "  full-start     전체 서버 시작 (API + Web)"
    echo "  full-stop      전체 서버 중지"
    echo ""
    echo "Options:"
    echo "  --production   프로덕션 모드로 실행"
    echo "  --help         이 도움말 표시"
    echo ""
    echo "Examples:"
    echo "  $0 start-api              # FastAPI 서버 시작"
    echo "  $0 start-api --production # 프로덕션 모드로 FastAPI 서버 시작"
    echo "  $0 full-start            # 전체 서버 시작"
}

check_dependencies() {
    echo -e "${YELLOW}의존성 확인 중...${NC}"
    
    # Python 의존성 확인
    if [ -f "$BACKEND_DIR/requirements.txt" ]; then
        echo "📦 Python 의존성 설치 중..."
        cd "$BACKEND_DIR"
        pip install -q -r requirements.txt
        echo "✅ Python 의존성 설치 완료"
    fi
    
    # Node.js 의존성 확인
    if [ -f "$FRONTEND_DIR/package.json" ]; then
        echo "📦 Node.js 의존성 확인 중..."
        cd "$FRONTEND_DIR"
        if [ ! -d "node_modules" ]; then
            echo "Node.js 의존성 설치 중..."
            npm install
            echo "✅ Node.js 의존성 설치 완료"
        else
            echo "✅ Node.js 의존성 이미 설치됨"
        fi
    fi
}

start_api() {
    local production=$1
    
    echo -e "${GREEN}🚀 FastAPI 서버 시작 중...${NC}"
    
    cd "$BACKEND_DIR"
    
    if [ "$production" = "true" ]; then
        python run_server.py start --production
    else
        python run_server.py start
    fi
}

stop_api() {
    echo -e "${YELLOW}🛑 FastAPI 서버 중지 중...${NC}"
    
    cd "$BACKEND_DIR"
    python run_server.py stop
}

restart_api() {
    local production=$1
    
    echo -e "${BLUE}🔄 FastAPI 서버 재시작 중...${NC}"
    
    cd "$BACKEND_DIR"
    
    if [ "$production" = "true" ]; then
        python run_server.py restart --production
    else
        python run_server.py restart
    fi
}

status_api() {
    echo -e "${BLUE}📊 FastAPI 서버 상태 확인 중...${NC}"
    
    cd "$BACKEND_DIR"
    python run_server.py status
}

health_api() {
    echo -e "${BLUE}🏥 FastAPI 서버 Health Check 중...${NC}"
    
    cd "$BACKEND_DIR"
    python run_server.py health
}

start_web() {
    echo -e "${GREEN}🌐 Next.js 웹 애플리케이션 시작 중...${NC}"
    
    cd "$FRONTEND_DIR"
    npm run dev
}

install_deps() {
    echo -e "${YELLOW}📦 의존성 설치 중...${NC}"
    check_dependencies
    echo -e "${GREEN}✅ 모든 의존성 설치 완료${NC}"
}

full_start() {
    local production=$1
    
    echo -e "${GREEN}🚀 전체 서버 시작 중...${NC}"
    
    # 의존성 확인
    check_dependencies
    
    # FastAPI 서버 시작
    start_api "$production"
    
    # 잠시 대기
    sleep 3
    
    # Next.js 서버 시작 (백그라운드)
    echo -e "${GREEN}🌐 Next.js 서버 시작 중...${NC}"
    cd "$FRONTEND_DIR"
    npm run dev &
    
    echo -e "${GREEN}✅ 전체 서버 시작 완료!${NC}"
    echo ""
    echo "📍 FastAPI 서버: http://127.0.0.1:8000"
    echo "📍 Next.js 서버: http://localhost:3000"
    echo "📚 API 문서: http://127.0.0.1:8000/docs"
}

full_stop() {
    echo -e "${YELLOW}🛑 전체 서버 중지 중...${NC}"
    
    # FastAPI 서버 중지
    stop_api
    
    # Next.js 서버 중지
    echo "🛑 Next.js 서버 중지 중..."
    pkill -f "next-server" || true
    pkill -f "npm.*dev" || true
    
    echo -e "${GREEN}✅ 전체 서버 중지 완료${NC}"
}

# 메인 로직
PRODUCTION=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --production)
            PRODUCTION=true
            shift
            ;;
        --help)
            print_help
            exit 0
            ;;
        *)
            COMMAND=$1
            shift
            ;;
    esac
done

case $COMMAND in
    start-api)
        start_api "$PRODUCTION"
        ;;
    stop-api)
        stop_api
        ;;
    restart-api)
        restart_api "$PRODUCTION"
        ;;
    status-api)
        status_api
        ;;
    health-api)
        health_api
        ;;
    start-web)
        start_web
        ;;
    install-deps)
        install_deps
        ;;
    full-start)
        full_start "$PRODUCTION"
        ;;
    full-stop)
        full_stop
        ;;
    *)
        echo -e "${RED}❌ 알 수 없는 명령어: $COMMAND${NC}"
        echo ""
        print_help
        exit 1
        ;;
esac 