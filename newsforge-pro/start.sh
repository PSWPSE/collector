#!/bin/bash

# NewsForge Pro 시작 스크립트
echo "🚀 NewsForge Pro 시작 중..."
echo "================================================="

# 옵션 파싱
DEVELOPMENT=false
PRODUCTION=false
DOCKER=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --dev|--development)
      DEVELOPMENT=true
      shift
      ;;
    --prod|--production)
      PRODUCTION=true
      shift
      ;;
    --docker)
      DOCKER=true
      shift
      ;;
    -h|--help)
      echo "사용법: $0 [옵션]"
      echo ""
      echo "옵션:"
      echo "  --dev, --development    개발 모드로 실행"
      echo "  --prod, --production    프로덕션 모드로 실행"
      echo "  --docker               Docker 환경으로 실행"
      echo "  -h, --help             도움말 표시"
      exit 0
      ;;
    *)
      echo "알 수 없는 옵션: $1"
      echo "도움말: $0 --help"
      exit 1
      ;;
  esac
done

# 기본값: 개발 모드
if [[ "$DEVELOPMENT" == false && "$PRODUCTION" == false && "$DOCKER" == false ]]; then
    DEVELOPMENT=true
fi

# Docker 모드
if [[ "$DOCKER" == true ]]; then
    echo "🐳 Docker 환경으로 시작..."
    
    # Docker Compose 실행
    docker-compose up --build
    
    exit 0
fi

# 개발 모드
if [[ "$DEVELOPMENT" == true ]]; then
    echo "🔧 개발 모드로 시작..."
    
    # 백엔드 환경 설정
    cd backend
    
    # 가상환경이 없다면 생성
    if [ ! -d "venv" ]; then
        echo "📦 가상환경 생성 중..."
        bash setup.sh
    else
        echo "✅ 가상환경 이미 존재"
        source venv/bin/activate
    fi
    
    # 구조 테스트
    echo "🧪 시스템 테스트 실행 중..."
    python test_structure.py
    
    if [ $? -eq 0 ]; then
        echo "✅ 테스트 통과!"
        echo "🚀 FastAPI 서버 시작 중..."
        python run_server.py
    else
        echo "❌ 테스트 실패. 환경을 확인해주세요."
        exit 1
    fi
    
    exit 0
fi

# 프로덕션 모드
if [[ "$PRODUCTION" == true ]]; then
    echo "🎯 프로덕션 모드로 시작..."
    
    # 환경 변수 확인
    if [ -z "$DATABASE_URL" ]; then
        echo "❌ DATABASE_URL 환경변수가 설정되지 않았습니다."
        exit 1
    fi
    
    if [ -z "$REDIS_URL" ]; then
        echo "❌ REDIS_URL 환경변수가 설정되지 않았습니다."
        exit 1
    fi
    
    # 프로덕션 서버 실행
    cd backend
    source venv/bin/activate
    
    echo "🚀 프로덕션 서버 시작 중..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
    
    exit 0
fi

echo "================================================="
echo "🎉 NewsForge Pro 시작 완료!" 