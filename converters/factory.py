"""
컨버터 팩토리

API 키 상태에 따라 적절한 변환기를 자동으로 선택하는 팩토리 클래스입니다.
"""

import os
from typing import Type, Optional
from dotenv import load_dotenv

from .base_converter import BaseConverter
from .anthropic_converter import AnthropicConverter
from .openai_converter import OpenAIConverter
from .local_converter import LocalConverter


class ConverterFactory:
    """변환기 팩토리 클래스"""
    
    def __init__(self):
        """팩토리 초기화"""
        load_dotenv()
        
    def _test_api_key(self, api_key: str, api_type: str) -> bool:
        """
        API 키 유효성 검사
        
        Args:
            api_key: 테스트할 API 키
            api_type: API 타입 ('anthropic' 또는 'openai')
            
        Returns:
            API 키가 유효한지 여부
        """
        if not api_key or len(api_key) < 10:
            return False
        
        try:
            if api_type == 'anthropic':
                # Anthropic API 키 형식 확인
                if not api_key.startswith('sk-ant-'):
                    return False
                # 간단한 API 호출 테스트
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                # 매우 짧은 테스트 요청
                response = client.messages.create(
                    model="claude-3-haiku-20240307",  # 빠른 모델 사용
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                return True
                
            elif api_type == 'openai':
                # OpenAI API 키 형식 확인
                if not api_key.startswith('sk-'):
                    return False
                # 간단한 API 호출 테스트
                from openai import OpenAI
                client = OpenAI(api_key=api_key)
                # 매우 짧은 테스트 요청
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",  # 빠른 모델 사용
                    max_tokens=10,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                return True
                
        except Exception as e:
            print(f"⚠️  API 키 테스트 실패 ({api_type}): {str(e)}")
            return False
        
        return False
    
    def get_available_converters(self) -> dict:
        """
        사용 가능한 변환기 목록 반환
        
        Returns:
            변환기 타입별 가용성 딕셔너리
        """
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        return {
            'anthropic': {
                'available': bool(anthropic_key),
                'valid': self._test_api_key(anthropic_key, 'anthropic') if anthropic_key else False,
                'description': 'Anthropic Claude API (최고 품질)'
            },
            'openai': {
                'available': bool(openai_key),
                'valid': self._test_api_key(openai_key, 'openai') if openai_key else False,
                'description': 'OpenAI GPT API (고품질)'
            },
            'local': {
                'available': True,
                'valid': True,
                'description': '로컬 규칙 기반 (API 불필요)'
            }
        }
    
    def create_converter(self, converter_type: Optional[str] = None, 
                        output_dir: str = 'converted_articles') -> BaseConverter:
        """
        변환기 생성
        
        Args:
            converter_type: 강제 지정할 변환기 타입 ('anthropic', 'openai', 'local')
            output_dir: 출력 디렉토리
            
        Returns:
            적절한 변환기 인스턴스
        """
        # 강제 지정된 경우
        if converter_type:
            return self._create_specific_converter(converter_type, output_dir)
        
        # 자동 선택
        return self._create_best_converter(output_dir)
    
    def _create_specific_converter(self, converter_type: str, output_dir: str) -> BaseConverter:
        """
        특정 변환기 생성
        
        Args:
            converter_type: 변환기 타입
            output_dir: 출력 디렉토리
            
        Returns:
            지정된 변환기 인스턴스
        """
        try:
            if converter_type == 'anthropic':
                return AnthropicConverter(output_dir)
            elif converter_type == 'openai':
                return OpenAIConverter(output_dir)
            elif converter_type == 'local':
                return LocalConverter(output_dir)
            else:
                raise ValueError(f"Unknown converter type: {converter_type}")
        except Exception as e:
            print(f"⚠️  {converter_type} 변환기 생성 실패: {str(e)}")
            print("🔄 로컬 변환기로 대체합니다.")
            return LocalConverter(output_dir)
    
    def _create_best_converter(self, output_dir: str) -> BaseConverter:
        """
        최적의 변환기 자동 선택 및 생성
        
        Args:
            output_dir: 출력 디렉토리
            
        Returns:
            최적의 변환기 인스턴스
        """
        available_converters = self.get_available_converters()
        
        # 우선순위: Anthropic > OpenAI > Local
        priority_order = ['anthropic', 'openai', 'local']
        
        for converter_type in priority_order:
            converter_info = available_converters[converter_type]
            
            if converter_info['available'] and converter_info['valid']:
                try:
                    converter = self._create_specific_converter(converter_type, output_dir)
                    print(f"✅ {converter_info['description']} 선택됨")
                    return converter
                except Exception as e:
                    print(f"⚠️  {converter_type} 변환기 생성 실패: {str(e)}")
                    continue
        
        # 모든 변환기 생성 실패 시 로컬 변환기 강제 사용
        print("🔄 모든 API 변환기 실패, 로컬 변환기를 사용합니다.")
        return LocalConverter(output_dir)
    
    def print_status(self) -> None:
        """변환기 상태 출력"""
        print("\n🔍 변환기 상태 확인:")
        print("=" * 50)
        
        available_converters = self.get_available_converters()
        
        for converter_type, info in available_converters.items():
            status_icon = "✅" if info['valid'] else "❌"
            availability = "사용 가능" if info['valid'] else "사용 불가"
            
            print(f"{status_icon} {converter_type.upper()}: {availability}")
            print(f"   {info['description']}")
            
            if converter_type != 'local' and info['available'] and not info['valid']:
                print(f"   ⚠️  API 키가 설정되었지만 유효하지 않습니다.")
            elif converter_type != 'local' and not info['available']:
                print(f"   ⚠️  API 키가 설정되지 않았습니다.")
        
        print("=" * 50)
    
    def get_recommended_converter(self) -> str:
        """
        추천 변환기 타입 반환
        
        Returns:
            추천 변환기 타입
        """
        available_converters = self.get_available_converters()
        
        if available_converters['anthropic']['valid']:
            return 'anthropic'
        elif available_converters['openai']['valid']:
            return 'openai'
        else:
            return 'local'


# 편의를 위한 전역 팩토리 인스턴스
converter_factory = ConverterFactory()


def create_converter(converter_type: Optional[str] = None, 
                    output_dir: str = 'converted_articles') -> BaseConverter:
    """
    변환기 생성 편의 함수
    
    Args:
        converter_type: 변환기 타입 (None이면 자동 선택)
        output_dir: 출력 디렉토리
        
    Returns:
        변환기 인스턴스
    """
    return converter_factory.create_converter(converter_type, output_dir)


def print_converter_status():
    """변환기 상태 출력 편의 함수"""
    converter_factory.print_status()


def get_available_converters():
    """사용 가능한 변환기 목록 반환 편의 함수"""
    return converter_factory.get_available_converters() 