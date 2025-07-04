"""
대량 뉴스 기사 추출 모듈

뉴스 사이트에서 여러 뉴스 기사를 자동으로 찾아서 추출합니다.
"""

try:
    from .yahoo_news_extractor import YahooNewsExtractor
    __all__ = ['YahooNewsExtractor']
except ImportError:
    __all__ = [] 