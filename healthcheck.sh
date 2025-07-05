#!/bin/bash

# 🔍 NewsForge Pro Health Check Script
set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 헬스 체크 함수
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    local timeout=${4:-5}
    
    echo -e "${BLUE}🔍 Checking $service_name...${NC}"
    
    if curl -f -m $timeout http://localhost:$port$endpoint >/dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name: Healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name: Unhealthy${NC}"
        return 1
    fi
}

# 메인 헬스 체크
main_healthcheck() {
    echo -e "${BLUE}🚀 Starting comprehensive health check...${NC}"
    
    local failures=0
    
    # API 서비스 체크
    if ! check_service "API Service" 8000 "/api/v1/health"; then
        failures=$((failures + 1))
    fi
    
    # Web 서비스 체크
    if ! check_service "Web Service" 3000 "/"; then
        failures=$((failures + 1))
    fi
    
    # 추가 시스템 체크
    echo -e "${BLUE}🔍 Checking system resources...${NC}"
    
    # 메모리 사용량 체크
    memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    if (( $(echo "$memory_usage > 85" | bc -l) )); then
        echo -e "${RED}❌ High memory usage: ${memory_usage}%${NC}"
        failures=$((failures + 1))
    else
        echo -e "${GREEN}✅ Memory usage: ${memory_usage}%${NC}"
    fi
    
    # 디스크 사용량 체크
    disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 85 ]; then
        echo -e "${RED}❌ High disk usage: ${disk_usage}%${NC}"
        failures=$((failures + 1))
    else
        echo -e "${GREEN}✅ Disk usage: ${disk_usage}%${NC}"
    fi
    
    # 전체 결과
    if [ $failures -eq 0 ]; then
        echo -e "${GREEN}🎉 All health checks passed!${NC}"
        exit 0
    else
        echo -e "${RED}❌ $failures health check(s) failed!${NC}"
        exit 1
    fi
}

# 도커 헬스 체크 (간단 버전)
docker_healthcheck() {
    if curl -f http://localhost:8000/api/v1/health >/dev/null 2>&1; then
        exit 0
    else
        exit 1
    fi
}

# 인자에 따른 실행
case "${1:-main}" in
    "docker")
        docker_healthcheck
        ;;
    "main"|*)
        main_healthcheck
        ;;
esac 