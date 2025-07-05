"""
뉴스 변환기 패키지

이 패키지는 다양한 방식으로 뉴스 기사를 마크다운으로 변환하는 도구들을 포함합니다.

- anthropic: Anthropic Claude API 기반 변환
- openai: OpenAI GPT API 기반 변환  
- local: API 없이 로컬에서 작동하는 변환
- factory: 상황에 맞는 변환기 자동 선택
"""

try:
    from .factory import ConverterFactory
    from .anthropic_converter import AnthropicConverter
    from .openai_converter import OpenAIConverter
    from .local_converter import LocalConverter
    
    __all__ = [
        'ConverterFactory',
        'AnthropicConverter', 
        'OpenAIConverter',
        'LocalConverter'
    ]
except ImportError:
    # 개발 중이거나 의존성이 설치되지 않은 경우
    __all__ = [] 