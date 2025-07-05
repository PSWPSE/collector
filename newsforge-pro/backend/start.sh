#!/bin/bash

# NewsForge Pro 빠른 서버 시작 스크립트

echo "🚀 NewsForge Pro 서버 시작..."

# 현재 디렉토리를 backend로 변경
cd "$(dirname "$0")"

# Python 의존성 설치 (필요한 경우)
echo "📦 의존성 확인 중..."
pip install -q psutil requests 2>/dev/null || true

# 서버 시작
echo "🔧 서버 시작 중..."
python run_server.py start

echo "✅ 서버 시작 완료!"
echo "📍 Health Check: http://127.0.0.1:8000/api/v1/health"
echo "📚 API 문서: http://127.0.0.1:8000/docs" 