#!/bin/bash
# NewsForge Pro 백엔드 설정 스크립트

echo "🚀 NewsForge Pro 백엔드 환경 설정 시작"
echo "================================================="

# 가상환경 생성
echo "📦 가상환경 생성 중..."
python3 -m venv venv

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치
echo "📋 의존성 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

# 구조 테스트 실행
echo "🧪 구조 테스트 실행 중..."
python test_structure.py

# 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ 환경 설정 완료!"
    echo "📍 서버 실행: python run_server.py"
    echo "📍 API 문서: http://localhost:8000/api/docs"
else
    echo "❌ 환경 설정 중 오류 발생"
    exit 1
fi

echo "================================================="
echo "🎉 NewsForge Pro 백엔드 준비 완료!" 