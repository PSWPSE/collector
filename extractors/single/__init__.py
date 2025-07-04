"""
단일 뉴스 기사 추출 모듈

웹 URL을 입력받아 해당 페이지의 뉴스 기사 하나를 추출합니다.
"""

try:
    from .web_extractor import WebExtractor
    __all__ = ['WebExtractor']
except ImportError:
    __all__ = [] 