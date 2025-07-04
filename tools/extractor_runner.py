#!/usr/bin/env python3
"""
웹 콘텐츠 추출기 통합 실행 스크립트

이 스크립트를 통해 다음 기능을 선택할 수 있습니다:
1. 단일 뉴스 기사 추출 (URL 입력)
2. Yahoo Finance 뉴스 대량 추출
3. 추출된 TXT 파일을 마크다운으로 변환
"""

import sys
import os
from typing import Optional

# 프로젝트 루트 경로를 Python path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extractors.single.web_extractor import WebExtractor
from extractors.bulk.yahoo_news_extractor import YahooNewsExtractor

def print_banner():
    """프로그램 배너 출력"""
    print("=" * 60)
    print("🌐 웹 콘텐츠 추출기 & 마크다운 변환기")
    print("=" * 60)
    print()

def print_menu():
    """메뉴 출력"""
    print("📋 사용 가능한 기능:")
    print("1. 단일 뉴스 기사 추출 (URL 입력)")
    print("2. Yahoo Finance 뉴스 대량 추출")
    print("3. 추출된 TXT 파일을 마크다운으로 변환")
    print("4. 프로그램 종료")
    print()

def extract_single_news():
    """단일 뉴스 기사 추출"""
    print("\n🔍 단일 뉴스 기사 추출")
    print("-" * 30)
    
    url = input("📰 뉴스 기사 URL을 입력하세요: ").strip()
    
    if not url:
        print("❌ URL이 입력되지 않았습니다.")
        return
    
    if not url.startswith(('http://', 'https://')):
        print("❌ 유효한 URL을 입력해주세요. (http:// 또는 https://로 시작)")
        return
    
    print(f"🚀 추출 시작: {url}")
    
    # Selenium 사용 여부 확인
    use_selenium = input("🤖 Selenium을 사용하시겠습니까? (동적 콘텐츠가 있는 사이트의 경우 권장) [y/N]: ").strip().lower()
    selenium_mode = use_selenium in ['y', 'yes', '1']
    
    extractor = WebExtractor(use_selenium=selenium_mode, save_to_file=True)
    
    try:
        result = extractor.extract_data(url)
        
        if result['success']:
            print("✅ 추출 성공!")
            print(f"📁 저장 위치: extracted_articles/")
            print(f"📄 제목: {result['title']}")
            print(f"👤 저자: {result.get('author', 'Unknown')}")
            print(f"📅 발행일: {result.get('publish_date', 'Unknown')}")
        else:
            print(f"❌ 추출 실패: {result['error']}")
    
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    finally:
        extractor.close()

def extract_bulk_news():
    """대량 뉴스 추출"""
    print("\n📰 Yahoo Finance 뉴스 대량 추출")
    print("-" * 40)
    
    # 추출할 기사 수 입력
    try:
        max_articles = input("📊 추출할 기사 수를 입력하세요 (기본값: 10): ").strip()
        max_articles = int(max_articles) if max_articles else 10
        
        if max_articles <= 0:
            print("❌ 1개 이상의 기사 수를 입력해주세요.")
            return
            
    except ValueError:
        print("❌ 유효한 숫자를 입력해주세요.")
        return
    
    print(f"🚀 Yahoo Finance에서 최대 {max_articles}개 기사 추출 시작...")
    
    extractor = YahooNewsExtractor()
    
    try:
        results = extractor.extract_all_news(max_articles=max_articles)
        
        print(f"\n📊 추출 결과:")
        success_count = sum(1 for r in results if r['success'])
        print(f"✅ 성공: {success_count}/{len(results)}개")
        
        if results:
            print(f"\n📝 추출된 기사 목록:")
            for i, result in enumerate(results, 1):
                status = "✅" if result['success'] else "❌"
                title = result['title'][:50] + "..." if len(result['title']) > 50 else result['title']
                print(f"{i:2d}. {status} {title}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
    
    finally:
        extractor.close()

def convert_to_markdown():
    """TXT 파일을 마크다운으로 변환"""
    print("\n📝 TXT → 마크다운 변환")
    print("-" * 30)
    
    # converter.py 파일 존재 확인
    converter_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'converter.py')
    
    if not os.path.exists(converter_path):
        print("❌ converter.py 파일을 찾을 수 없습니다.")
        print(f"📁 예상 위치: {converter_path}")
        return
    
    print("🔍 extracted_articles 폴더에서 TXT 파일을 찾는 중...")
    
    extracted_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'extracted_articles')
    
    if not os.path.exists(extracted_dir):
        print("❌ extracted_articles 폴더를 찾을 수 없습니다.")
        return
    
    # TXT 파일 목록 가져오기
    txt_files = [f for f in os.listdir(extracted_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print("❌ 변환할 TXT 파일이 없습니다.")
        print("💡 먼저 뉴스 기사를 추출해주세요.")
        return
    
    print(f"📄 {len(txt_files)}개의 TXT 파일을 찾았습니다.")
    
    # 변환 방식 선택
    print("\n🔄 변환 방식을 선택하세요:")
    print("1. 모든 파일 변환")
    print("2. 특정 파일 선택")
    
    choice = input("선택 (1-2): ").strip()
    
    if choice == '1':
        # 모든 파일 변환
        print("🚀 모든 TXT 파일을 마크다운으로 변환 중...")
        os.system(f"cd {os.path.dirname(converter_path)} && python converter.py --all")
    
    elif choice == '2':
        # 파일 목록 표시
        print("\n📋 변환 가능한 파일:")
        for i, filename in enumerate(txt_files, 1):
            print(f"{i:2d}. {filename}")
        
        try:
            file_num = int(input("\n변환할 파일 번호를 입력하세요: ").strip())
            if 1 <= file_num <= len(txt_files):
                selected_file = txt_files[file_num - 1]
                file_path = os.path.join(extracted_dir, selected_file)
                print(f"🚀 {selected_file} 파일을 마크다운으로 변환 중...")
                os.system(f"cd {os.path.dirname(converter_path)} && python converter.py '{file_path}'")
            else:
                print("❌ 유효한 파일 번호를 입력해주세요.")
        except ValueError:
            print("❌ 유효한 숫자를 입력해주세요.")
    
    else:
        print("❌ 유효한 선택지를 입력해주세요.")

def main():
    """메인 실행 함수"""
    print_banner()
    
    while True:
        print_menu()
        
        try:
            choice = input("🎯 원하는 기능을 선택하세요 (1-4): ").strip()
            
            if choice == '1':
                extract_single_news()
            elif choice == '2':
                extract_bulk_news()
            elif choice == '3':
                convert_to_markdown()
            elif choice == '4':
                print("👋 프로그램을 종료합니다.")
                break
            else:
                print("❌ 유효한 선택지를 입력해주세요. (1-4)")
            
            print("\n" + "="*60)
            input("⏸️  계속하려면 Enter를 누르세요...")
            print()
            
        except KeyboardInterrupt:
            print("\n\n👋 프로그램을 종료합니다.")
            break
        except Exception as e:
            print(f"❌ 예상치 못한 오류가 발생했습니다: {str(e)}")

if __name__ == "__main__":
    main() 