"""
NewsForge Pro 커스텀 예외 정의
"""

from typing import Optional

class NewsForgeException(Exception):
    """NewsForge 기본 예외"""
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ExtractionException(NewsForgeException):
    """뉴스 추출 실패 예외"""
    pass

class ConversionException(NewsForgeException):
    """AI 변환 실패 예외"""
    pass

class RateLimitException(NewsForgeException):
    """사용량 제한 초과 예외"""
    pass

class UsageLimitException(NewsForgeException):
    """일일/월간 사용량 제한 초과 예외"""
    pass

class AuthenticationException(NewsForgeException):
    """인증 실패 예외"""
    pass

class PermissionException(NewsForgeException):
    """권한 부족 예외"""
    pass

class ValidationException(NewsForgeException):
    """입력 검증 실패 예외"""
    pass

class ServiceUnavailableException(NewsForgeException):
    """서비스 일시 불가 예외"""
    pass 