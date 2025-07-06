"""
중앙집중식 API 키 관리 시스템
모든 API 키는 이 파일을 통해서만 접근
"""

import os
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import json


class ApiKeyManager:
    """API 키 중앙 관리 클래스"""
    
    def __init__(self):
        self._encryption_key = self._get_encryption_key()
        self._cipher = Fernet(self._encryption_key)
        self._cached_keys: Dict[str, str] = {}
    
    def _get_encryption_key(self) -> bytes:
        """암호화 키 생성 또는 로드"""
        key_str = os.getenv('ENCRYPTION_KEY')
        if key_str:
            return key_str.encode()
        
        # 개발 환경용 기본 키 (프로덕션에서는 반드시 설정 필요)
        return Fernet.generate_key()
    
    def get_openai_key(self, user_key: Optional[str] = None) -> str:
        """OpenAI API 키 반환 (사용자 키 우선, 환경변수 fallback)"""
        if user_key:
            # 사용자 제공 키 검증
            if self._validate_openai_key(user_key):
                return user_key
            else:
                raise ValueError("Invalid OpenAI API key format")
        
        # 환경변수에서 가져오기
        env_key = os.getenv('OPENAI_API_KEY')
        if env_key and env_key != 'your_key_here':
            return env_key
        
        raise ValueError("No valid OpenAI API key available")
    
    def get_anthropic_key(self, user_key: Optional[str] = None) -> str:
        """Anthropic API 키 반환 (사용자 키 우선, 환경변수 fallback)"""
        if user_key:
            # 사용자 제공 키 검증
            if self._validate_anthropic_key(user_key):
                return user_key
            else:
                raise ValueError("Invalid Anthropic API key format")
        
        # 환경변수에서 가져오기
        env_key = os.getenv('ANTHROPIC_API_KEY')
        if env_key and env_key != 'your_key_here':
            return env_key
        
        raise ValueError("No valid Anthropic API key available")
    
    def _validate_openai_key(self, key: str) -> bool:
        """OpenAI API 키 형식 검증"""
        return key.startswith('sk-') and len(key) > 20
    
    def _validate_anthropic_key(self, key: str) -> bool:
        """Anthropic API 키 형식 검증"""
        return key.startswith('sk-ant-') and len(key) > 30
    
    def encrypt_key(self, key: str) -> str:
        """API 키 암호화"""
        return self._cipher.encrypt(key.encode()).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """API 키 복호화"""
        return self._cipher.decrypt(encrypted_key.encode()).decode()
    
    def get_key_info(self, provider: str, user_key: Optional[str] = None) -> Dict[str, Any]:
        """API 키 정보 반환"""
        try:
            if provider == 'openai':
                key = self.get_openai_key(user_key)
            elif provider == 'anthropic':
                key = self.get_anthropic_key(user_key)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            return {
                'provider': provider,
                'available': True,
                'key_length': len(key),
                'key_prefix': key[:10] + '...' if len(key) > 10 else key,
                'source': 'user' if user_key else 'environment'
            }
        except ValueError as e:
            return {
                'provider': provider,
                'available': False,
                'error': str(e),
                'source': None
            }


# 전역 인스턴스
api_key_manager = ApiKeyManager()


# 편의 함수들
def get_openai_key(user_key: Optional[str] = None) -> str:
    """OpenAI API 키 가져오기"""
    return api_key_manager.get_openai_key(user_key)


def get_anthropic_key(user_key: Optional[str] = None) -> str:
    """Anthropic API 키 가져오기"""
    return api_key_manager.get_anthropic_key(user_key)


def validate_api_key(key: str, provider: str) -> bool:
    """API 키 검증"""
    if provider == 'openai':
        return api_key_manager._validate_openai_key(key)
    elif provider == 'anthropic':
        return api_key_manager._validate_anthropic_key(key)
    return False


def get_all_available_keys() -> Dict[str, Dict[str, Any]]:
    """사용 가능한 모든 API 키 정보 반환"""
    return {
        'openai': api_key_manager.get_key_info('openai'),
        'anthropic': api_key_manager.get_key_info('anthropic')
    } 