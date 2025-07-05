#!/usr/bin/env python3
"""
NewsForge Pro 백엔드 구조 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """모든 모듈 임포트 테스트"""
    print("🧪 모듈 임포트 테스트 시작...")
    
    try:
        # 스키마 임포트
        from app.schemas.conversion import ConversionRequest, ConversionResponse
        print("✅ 스키마 임포트 성공")
        
        # 예외 클래스 임포트
        from app.core.exceptions import NewsForgeException
        print("✅ 예외 클래스 임포트 성공")
        
        # 서비스 임포트
        from app.services.converter_service import ConverterService
        from app.services.rate_limiter import RateLimiter
        from app.services.user_service import UserService
        print("✅ 서비스 클래스 임포트 성공")
        
        # 인증 모듈 임포트
        from app.core.auth import create_mock_user
        print("✅ 인증 모듈 임포트 성공")
        
        return True
        
    except Exception as e:
        print(f"❌ 임포트 실패: {str(e)}")
        return False

def test_services():
    """서비스 초기화 테스트"""
    print("\n🔧 서비스 초기화 테스트 시작...")
    
    try:
        from app.services.converter_service import ConverterService
        from app.services.rate_limiter import RateLimiter
        from app.services.user_service import UserService
        
        # 서비스 인스턴스 생성
        converter = ConverterService()
        rate_limiter = RateLimiter()
        user_service = UserService()
        
        print("✅ 서비스 인스턴스 생성 성공")
        
        # 기본 메서드 테스트
        result = rate_limiter.plan_limits
        print(f"✅ Rate Limiter 설정 확인: {list(result.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ 서비스 초기화 실패: {str(e)}")
        return False

def test_schemas():
    """스키마 검증 테스트"""
    print("\n📋 스키마 검증 테스트 시작...")
    
    try:
        from app.schemas.conversion import ConversionRequest, PlatformType, ConverterType
        
        # 변환 요청 생성
        request = ConversionRequest(
            url="https://example.com/news",
            platforms=[PlatformType.TWITTER, PlatformType.THREADS],
            converter_type=ConverterType.AUTO
        )
        
        print(f"✅ 변환 요청 생성 성공: {request.url}")
        print(f"✅ 플랫폼: {request.platforms}")
        
        return True
        
    except Exception as e:
        print(f"❌ 스키마 검증 실패: {str(e)}")
        return False

def test_auth():
    """인증 모듈 테스트"""
    print("\n🔐 인증 모듈 테스트 시작...")
    
    try:
        from app.core.auth import create_mock_user, verify_token
        
        # 모의 사용자 생성
        user_info = create_mock_user("test@example.com", "premium")
        print(f"✅ 모의 사용자 생성: {user_info['user']['email']}")
        
        # 토큰 검증
        verified = verify_token(user_info['token'])
        if verified:
            print(f"✅ 토큰 검증 성공: {verified['name']}")
        else:
            print("❌ 토큰 검증 실패")
        
        return True
        
    except Exception as e:
        print(f"❌ 인증 테스트 실패: {str(e)}")
        return False

def main():
    """메인 테스트 실행"""
    print("🎯 NewsForge Pro 백엔드 구조 테스트")
    print("=" * 50)
    
    tests = [
        ("모듈 임포트", test_imports),
        ("서비스 초기화", test_services),
        ("스키마 검증", test_schemas),
        ("인증 모듈", test_auth)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} 테스트 중 오류: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}개 통과, {failed}개 실패")
    
    if failed == 0:
        print("🎉 모든 테스트 통과! 백엔드 구조가 올바르게 구성되었습니다.")
        return True
    else:
        print("⚠️  일부 테스트 실패. 구조를 확인하고 수정해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 