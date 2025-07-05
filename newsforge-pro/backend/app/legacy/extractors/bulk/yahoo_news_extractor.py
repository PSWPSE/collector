from ..single.web_extractor import WebExtractor
from bs4 import BeautifulSoup
import time
from typing import List, Dict, Any, Optional
import os
from datetime import datetime
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver

def sanitize_filename(title: str) -> str:
    """파일 이름에 사용할 수 없는 문자 제거"""
    # 파일명에 사용할 수 없는 문자를 언더스코어로 대체
    filename = re.sub(r'[<>:"/\\|?*]', '_', title)
    # 공백을 언더스코어로 대체
    filename = filename.replace(' ', '_')
    # 여러 개의 언더스코어를 하나로 통합
    filename = re.sub(r'_+', '_', filename)
    return filename[:100]  # 파일명 길이 제한

class YahooNewsExtractor:
    """Yahoo Finance 뉴스 대량 추출기"""
    
    def __init__(self, save_dir: str = 'extracted_articles'):
        self.save_dir = save_dir
        self.extractor = WebExtractor(use_selenium=True, save_to_file=False)
        os.makedirs(save_dir, exist_ok=True)
    
    def extract_news_links(self, driver: Optional[WebDriver]) -> List[Dict[str, str]]:
        """뉴스 링크와 제목 추출"""
        news_items = []
        
        # driver가 None인지 확인
        if driver is None:
            print("오류: 드라이버가 초기화되지 않았습니다.")
            return news_items
        
        # 뉴스 항목 대기 및 찾기
        wait = WebDriverWait(driver, 20)
        
        # 여러 CSS 선택자 시도
        selectors = [
            "div[data-test='content-list'] a[href*='/news/']",
            "ul.js-stream-content li a",
            "div.js-stream-content a",
            "div[class*='article'] a",
            "div[class*='story'] a"
        ]
        
        for selector in selectors:
            try:
                articles = wait.until(EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, selector)
                ))
                
                if articles:
                    print(f"뉴스 항목 발견: {selector}")
                    break
            except:
                continue
        else:
            print("경고: 기본 선택자로 시도합니다")
            articles = driver.find_elements(By.TAG_NAME, "a")
        
        for article in articles:
            try:
                href = article.get_attribute("href")
                title = article.text.strip()
                
                # 유효한 뉴스 링크 확인
                if (href and title and 
                    'finance.yahoo.com' in href and 
                    not any(x in href.lower() for x in ['video', 'podcast', 'photo']) and
                    len(title) > 20):  # 너무 짧은 제목 제외
                    
                    news_items.append({
                        'url': href,
                        'title': title
                    })
                    print(f"발견된 기사: {title[:50]}...")
                    
                    if len(news_items) >= 10:  # 최대 10개까지만 수집
                        break
                        
            except Exception as e:
                print(f"링크 추출 중 오류: {str(e)}")
                continue
        
        return news_items
    
    def extract_all_news(self, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Yahoo Finance에서 뉴스 기사들을 추출합니다."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results = []
        
        try:
            # Selenium 드라이버가 제대로 초기화되었는지 확인
            if self.extractor.driver is None:
                print("오류: Selenium 드라이버가 초기화되지 않았습니다.")
                return results
            
            # 메인 페이지에서 뉴스 링크 추출
            print("뉴스 링크 수집 중...")
            main_url = "https://finance.yahoo.com/topic/latest-news/"
            
            # 페이지 로딩 시도 (최대 3번 재시도)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    print(f"페이지 로딩 시도 {attempt + 1}/{max_retries}...")
                    self.extractor.driver.set_page_load_timeout(60)  # 60초 타임아웃 설정
                    self.extractor.driver.get(main_url)
                    print("페이지 로딩 성공!")
                    break
                except Exception as e:
                    print(f"페이지 로딩 실패 (시도 {attempt + 1}): {str(e)}")
                    if attempt < max_retries - 1:
                        print("5초 후 재시도...")
                        time.sleep(5)
                    else:
                        print("모든 시도 실패. 프로그램을 종료합니다.")
                        return results
            
            # 페이지 로딩 대기
            print("페이지 콘텐츠 로딩 대기 중...")
            time.sleep(10)  # 더 긴 대기 시간
            
            # 페이지 스크롤
            print("페이지 스크롤 중...")
            for i in range(3):  # 여러 번 스크롤
                print(f"스크롤 {i + 1}/3...")
                self.extractor.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)  # 스크롤 후 대기 시간 증가
            
            news_links = self.extract_news_links(self.extractor.driver)
            print(f"\n총 {len(news_links)}개의 뉴스 링크를 찾았습니다.")
            
            if not news_links:
                print("뉴스 링크를 찾을 수 없습니다. 다른 방법을 시도해보겠습니다.")
                # 대체 URL 시도
                alternative_urls = [
                    "https://finance.yahoo.com/news/",
                    "https://finance.yahoo.com/",
                    "https://finance.yahoo.com/quote/AAPL/news"
                ]
                
                for alt_url in alternative_urls:
                    try:
                        print(f"대체 URL 시도: {alt_url}")
                        self.extractor.driver.get(alt_url)
                        time.sleep(5)
                        news_links = self.extract_news_links(self.extractor.driver)
                        if news_links:
                            print(f"대체 URL에서 {len(news_links)}개의 뉴스를 찾았습니다.")
                            break
                    except Exception as e:
                        print(f"대체 URL 실패: {str(e)}")
                        continue
            
            # 각 뉴스 기사 추출
            for i, news in enumerate(news_links[:max_articles], 1):
                try:
                    print(f"\n[{i}/{len(news_links)}] 기사 추출 중: {news['title']}")
                    data = self.extractor.extract_data(news['url'])
                    
                    if data['success']:
                        # 파일명 생성
                        filename = f"{sanitize_filename(news['title'])}_{timestamp}.txt"
                        filepath = os.path.join(self.save_dir, filename)
                        
                        # 파일 저장
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(f"제목: {data['title']}\n")
                            f.write(f"URL: {news['url']}\n")
                            f.write(f"추출 시간: {data['timestamp']}\n")
                            f.write("="*80 + "\n\n")
                            
                            if data['metadata']:
                                f.write("메타 정보:\n")
                                for key, value in data['metadata'].items():
                                    f.write(f"{key}: {value}\n")
                                f.write("-"*80 + "\n\n")
                            
                            if data['author']:
                                f.write(f"저자: {data['author']}\n")
                            if data['publish_date']:
                                f.write(f"발행일: {data['publish_date']}\n")
                            f.write("\n본문:\n")
                            f.write(data['content']['text'])
                        
                        print(f"저장 완료: {filename}")
                        results.append({
                            'title': data['title'],
                            'url': news['url'],
                            'filename': filename,
                            'success': True
                        })
                    else:
                        print(f"추출 실패: {data['error']}")
                        results.append({
                            'title': news['title'],
                            'url': news['url'],
                            'error': data['error'],
                            'success': False
                        })
                    
                    time.sleep(3)  # 요청 간격 증가
                    
                except Exception as e:
                    print(f"기사 추출 중 오류 발생: {str(e)}")
                    results.append({
                        'title': news.get('title', 'Unknown'),
                        'url': news.get('url', 'Unknown'),
                        'error': str(e),
                        'success': False
                    })
                    continue
                
        finally:
            self.extractor.close()
            print(f"\n추출 완료! 저장 위치: {self.save_dir}")
        
        return results
    
    def close(self):
        """리소스 정리"""
        if self.extractor:
            self.extractor.close()

def main():
    """메인 실행 함수 (하위 호환성을 위해 유지)"""
    extractor = YahooNewsExtractor()
    results = extractor.extract_all_news()
    
    print(f"\n=== 추출 결과 ===")
    success_count = sum(1 for r in results if r['success'])
    print(f"성공: {success_count}/{len(results)}개")
    
    if results:
        print("\n추출된 기사:")
        for i, result in enumerate(results, 1):
            status = "✓" if result['success'] else "✗"
            print(f"{i}. {status} {result['title']}")

if __name__ == "__main__":
    main() 