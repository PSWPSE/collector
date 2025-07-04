# 웹 콘텐츠 추출기 가이드

## 📁 프로젝트 구조

```
collector/
├── extractors/                    # 추출기 패키지
│   ├── single/                   # 단일 뉴스 추출
│   │   ├── __init__.py
│   │   └── web_extractor.py     # 웹 추출기 클래스
│   └── bulk/                    # 대량 뉴스 추출
│       ├── __init__.py
│       └── yahoo_news_extractor.py  # Yahoo 뉴스 추출기
├── tools/                       # 도구 스크립트
│   └── extractor_runner.py      # 통합 실행 스크립트
├── extracted_articles/          # 추출된 TXT 파일
├── converted_articles/          # 변환된 마크다운 파일
└── converter.py                 # 마크다운 변환기
```

## 🚀 빠른 시작

### 1. 통합 실행 스크립트 사용 (권장)

```bash
python tools/extractor_runner.py
```

이 스크립트를 실행하면 다음 기능을 선택할 수 있습니다:
- 단일 뉴스 기사 추출 (URL 입력)
- Yahoo Finance 뉴스 대량 추출
- 추출된 TXT 파일을 마크다운으로 변환

### 2. 개별 모듈 직접 사용

#### 단일 뉴스 추출
```python
from extractors.single.web_extractor import WebExtractor

# 기본 추출 (requests 사용)
extractor = WebExtractor(use_selenium=False, save_to_file=True)
result = extractor.extract_data("https://example.com/news-article")
extractor.close()

# Selenium 사용 (동적 콘텐츠)
extractor = WebExtractor(use_selenium=True, save_to_file=True)
result = extractor.extract_data("https://example.com/news-article")
extractor.close()
```

#### 대량 뉴스 추출
```python
from extractors.bulk.yahoo_news_extractor import YahooNewsExtractor

# Yahoo Finance 뉴스 추출
extractor = YahooNewsExtractor(save_dir='my_articles')
results = extractor.extract_all_news(max_articles=5)
extractor.close()

# 결과 확인
for result in results:
    if result['success']:
        print(f"✅ {result['title']}")
    else:
        print(f"❌ {result['title']}: {result['error']}")
```

## 📋 기능별 상세 설명

### 🔍 단일 뉴스 추출기 (WebExtractor)

**용도**: 특정 뉴스 기사 URL을 입력받아 해당 기사의 내용을 추출

**특징**:
- requests 또는 Selenium 선택 가능
- 제목, 본문, 저자, 발행일, 메타데이터 추출
- 자동 파일 저장 기능
- 다양한 뉴스 사이트 지원

**사용 시나리오**:
- 특정 기사를 정확히 추출하고 싶을 때
- 정적 콘텐츠 사이트에서 빠른 추출이 필요할 때
- 동적 콘텐츠 사이트에서 Selenium이 필요할 때

### 📰 대량 뉴스 추출기 (YahooNewsExtractor)

**용도**: Yahoo Finance 뉴스 페이지에서 여러 뉴스 기사를 자동으로 찾아서 추출

**특징**:
- 자동 뉴스 링크 탐지
- 배치 처리로 여러 기사 동시 추출
- 진행 상황 실시간 표시
- 실패한 기사 추적 및 보고

**사용 시나리오**:
- 최신 뉴스를 대량으로 수집하고 싶을 때
- 정기적인 뉴스 모니터링이 필요할 때
- 특정 주제의 뉴스를 일괄 수집할 때

## ⚙️ 설정 및 옵션

### WebExtractor 옵션

```python
WebExtractor(
    use_selenium=False,    # Selenium 사용 여부
    save_to_file=True      # 자동 파일 저장 여부
)
```

### YahooNewsExtractor 옵션

```python
YahooNewsExtractor(
    save_dir='extracted_articles'  # 저장 디렉토리
)

# 추출 시 옵션
extractor.extract_all_news(
    max_articles=10  # 최대 추출 기사 수
)
```

## 🛠️ 고급 사용법

### 1. 커스텀 저장 디렉토리

```python
# 날짜별 폴더 생성
from datetime import datetime
today = datetime.now().strftime('%Y%m%d')
extractor = YahooNewsExtractor(save_dir=f'news_{today}')
```

### 2. 결과 데이터 활용

```python
# 추출 결과 분석
results = extractor.extract_all_news(max_articles=20)

successful = [r for r in results if r['success']]
failed = [r for r in results if not r['success']]

print(f"성공: {len(successful)}개")
print(f"실패: {len(failed)}개")

# 실패 원인 분석
for fail in failed:
    print(f"실패: {fail['title']} - {fail['error']}")
```

### 3. 에러 처리

```python
try:
    extractor = WebExtractor(use_selenium=True)
    result = extractor.extract_data(url)
    
    if result['success']:
        print(f"제목: {result['title']}")
        print(f"내용: {result['content']['text'][:200]}...")
    else:
        print(f"추출 실패: {result['error']}")
        
except Exception as e:
    print(f"예상치 못한 오류: {str(e)}")
finally:
    extractor.close()
```

## 📝 출력 파일 형식

### TXT 파일 구조
```
제목: [뉴스 제목]
URL: [원본 URL]
추출 시간: [ISO 형식 타임스탬프]
================================================================================

메타 정보:
description: [기사 설명]
author: [저자명]
published_time: [발행 시간]
keywords: [키워드]
--------------------------------------------------------------------------------

저자: [저자명]
발행일: [발행일]

본문:
[기사 본문 내용]
```

## 🔄 마크다운 변환

추출된 TXT 파일을 마크다운으로 변환:

```bash
# 통합 스크립트에서 선택
python tools/extractor_runner.py

# 직접 변환
python converter.py extracted_articles/article_20250101_120000.txt
python converter.py --all  # 모든 파일 변환
```

## 🚨 주의사항

### 1. 웹사이트 정책 준수
- 각 웹사이트의 robots.txt 및 이용약관을 확인하세요
- 과도한 요청으로 서버에 부하를 주지 않도록 주의하세요
- 추출 간격을 적절히 설정하세요

### 2. 리소스 관리
- 사용 후 반드시 `extractor.close()` 호출
- Selenium 사용 시 Chrome 드라이버 자동 관리
- 메모리 사용량 모니터링

### 3. 오류 처리
- 네트워크 오류에 대한 재시도 로직 구현
- 잘못된 URL에 대한 유효성 검사
- 추출 실패 시 로그 확인

## 📞 문제 해결

### 자주 발생하는 문제

1. **Chrome 드라이버 오류**
   ```bash
   pip install --upgrade webdriver-manager
   ```

2. **모듈 import 오류**
   ```bash
   # 프로젝트 루트에서 실행
   python -m tools.extractor_runner
   ```

3. **권한 오류**
   ```bash
   chmod +x tools/extractor_runner.py
   ```

4. **메모리 부족**
   - 한 번에 추출하는 기사 수를 줄이세요
   - 대량 추출 시 배치 처리 사용

### 로그 확인

추출 과정에서 발생하는 로그를 확인하여 문제를 진단할 수 있습니다:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔧 개발자 정보

- 단일 추출기: `extractors/single/web_extractor.py`
- 대량 추출기: `extractors/bulk/yahoo_news_extractor.py`
- 통합 실행기: `tools/extractor_runner.py`

각 모듈은 독립적으로 사용할 수 있으며, 필요에 따라 확장 가능합니다. 