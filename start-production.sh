#!/bin/bash

# 🚀 NewsForge Pro Production Startup Script
echo "🚀 Starting NewsForge Pro Production Services..."

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 디렉토리 생성
mkdir -p logs

# 가상환경 활성화 확인
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    echo -e "${GREEN}✅ Activating virtual environment...${NC}"
    source venv/bin/activate
fi

# 환경 변수 설정
export NODE_ENV=production
export PYTHONPATH=/Users/alphabridge/collector/newsforge-pro/backend

# PM2 설치 확인
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}⚠️ PM2 not found. Installing...${NC}"
    npm install -g pm2
fi

# 기존 프로세스 정리
echo -e "${BLUE}🔄 Stopping existing processes...${NC}"
pm2 delete all 2>/dev/null || true
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "next-server" 2>/dev/null || true

# 의존성 확인
echo -e "${BLUE}📦 Installing dependencies...${NC}"
pip install -r requirements.txt >/dev/null 2>&1

# Next.js 빌드 (production 모드)
echo -e "${BLUE}🏗️ Building Next.js application...${NC}"
cd news-to-social-web
npm install >/dev/null 2>&1
npm run build >/dev/null 2>&1
cd ..

# PM2로 서비스 시작
echo -e "${BLUE}🚀 Starting services with PM2...${NC}"
pm2 start ecosystem.config.js

# 서비스 상태 확인
echo -e "${BLUE}⏳ Waiting for services to initialize...${NC}"
sleep 15

# 헬스 체크
echo -e "${BLUE}🔍 Performing health checks...${NC}"

# API 헬스 체크
if curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
    echo -e "${GREEN}✅ API Service: Healthy${NC}"
else
    echo -e "${RED}❌ API Service: Unhealthy${NC}"
fi

# Web 헬스 체크
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Web Service: Healthy${NC}"
else
    echo -e "${RED}❌ Web Service: Unhealthy${NC}"
fi

# 서비스 상태 표시
echo -e "\n${GREEN}🎉 Services Status:${NC}"
pm2 status

echo -e "\n${BLUE}📱 Access URLs:${NC}"
echo -e "🌐 Web Service: ${GREEN}http://localhost:3000${NC}"
echo -e "🔗 API Service: ${GREEN}http://localhost:8000${NC}"
echo -e "📊 API Docs: ${GREEN}http://localhost:8000/docs${NC}"

echo -e "\n${YELLOW}💡 Management Commands:${NC}"
echo -e "📊 Status: ${BLUE}pm2 status${NC}"
echo -e "📋 Logs: ${BLUE}pm2 logs${NC}"
echo -e "🔄 Restart: ${BLUE}pm2 restart all${NC}"
echo -e "🛑 Stop: ${BLUE}pm2 stop all${NC}"
echo -e "🔥 Delete: ${BLUE}pm2 delete all${NC}"

echo -e "\n${GREEN}✅ Production services started successfully!${NC}" 