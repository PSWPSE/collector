#!/usr/bin/env python3
"""
뉴스 변환 통합 서비스

링크 URL을 입력하면 자동으로:
1. 뉴스 기사 추출 (URL → TXT)
2. 최적 변환기 선택 (API 키 상태 확인)
3. 마크다운 변환 (TXT → Markdown)

모든 과정이 한 번에 완료됩니다.
"""

import os
import sys
import argparse
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime

# 현재 스크립트의 디렉토리 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from extractors.single.web_extractor import WebExtractor
from converters.factory import create_converter, print_converter_status


class NewsConverterService:
    """뉴스 변환 통합 서비스"""
    
    def __init__(self, output_dir: str = 'converted_articles'):
        """
        서비스 초기화
        
        Args:
            output_dir: 최종 마크다운 출력 디렉토리
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 임시 디렉토리 생성
        self.temp_dir = Path('temp_extracted')
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        
        print("🚀 뉴스 변환 통합 서비스 시작")
    
    def _validate_url(self, url: str) -> bool:
        """
        URL 유효성 검사
        
        Args:
            url: 검사할 URL
            
        Returns:
            URL이 유효한지 여부
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _extract_article(self, url: str) -> Optional[Path]:
        """
        URL에서 뉴스 기사 추출
        
        Args:
            url: 뉴스 기사 URL
            
        Returns:
            추출된 TXT 파일 경로 (실패 시 None)
        """
        print(f"📰 뉴스 기사 추출 중: {url}")
        
        try:
            # Yahoo Finance 같은 동적 사이트는 Selenium 사용
            use_selenium = any(domain in url.lower() for domain in ['yahoo', 'finance', 'bloomberg', 'cnbc'])
            
            extractor = WebExtractor(use_selenium=use_selenium, save_to_file=False)
            data = extractor.extract_data(url)
            
            if data['success']:
                # TXT 파일 생성
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                txt_filename = f"article_{timestamp}.txt"
                txt_file = self.temp_dir / txt_filename
                
                # 텍스트 파일 작성
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(f"URL: {data['url']}\n")
                    f.write(f"제목: {data['title']}\n")
                    f.write(f"작성자: {data['author']}\n")
                    f.write(f"게시일: {data['publish_date']}\n")
                    f.write(f"추출일: {data['timestamp']}\n")
                    f.write("\n" + "="*50 + "\n\n")
                    
                    # 본문 내용 추출
                    content = data['content']
                    if isinstance(content, dict) and 'paragraphs' in content:
                        for paragraph in content['paragraphs']:
                            # paragraph가 문자열인 경우 (실제 WebExtractor 구조)
                            if isinstance(paragraph, str):
                                text = paragraph.strip()
                                if text:
                                    f.write(text + "\n\n")
                            # paragraph가 딕셔너리인 경우 (대안 구조)
                            elif isinstance(paragraph, dict) and 'text' in paragraph:
                                text = paragraph['text'].strip()
                                if text:
                                    f.write(text + "\n\n")
                    elif isinstance(content, str):
                        f.write(content)
                
                print(f"✅ 추출 완료: {txt_file.name}")
                return txt_file
            else:
                print("❌ 기사 추출 실패")
                return None
                
        except Exception as e:
            print(f"❌ 추출 중 오류 발생: {str(e)}")
            return None
        finally:
            # 리소스 정리
            if 'extractor' in locals():
                extractor.close()
    
    def _convert_article(self, txt_file: Path, converter_type: Optional[str] = None) -> Optional[Path]:
        """
        TXT 파일을 마크다운으로 변환
        
        Args:
            txt_file: 변환할 TXT 파일 경로
            converter_type: 사용할 변환기 타입 (None이면 자동 선택)
            
        Returns:
            변환된 마크다운 파일 경로 (실패 시 None)
        """
        print(f"🤖 마크다운 변환 중...")
        
        try:
            converter = create_converter(converter_type, str(self.output_dir))
            
            # 변환 실행
            converter.process_file(str(txt_file))
            
            # 생성된 마크다운 파일 찾기
            md_files = list(self.output_dir.glob(f"{txt_file.stem}_*_*.md"))
            
            if md_files:
                # 가장 최근 파일 선택
                latest_md = max(md_files, key=lambda f: f.stat().st_mtime)
                print(f"✅ 변환 완료: {latest_md.name}")
                return latest_md
            else:
                print("❌ 마크다운 파일 생성 실패")
                return None
                
        except Exception as e:
            print(f"❌ 변환 중 오류 발생: {str(e)}")
            return None
    
    def _cleanup_temp_file(self, txt_file: Path) -> None:
        """
        임시 TXT 파일 정리
        
        Args:
            txt_file: 삭제할 TXT 파일 경로
        """
        try:
            if txt_file.exists():
                txt_file.unlink()
                print(f"🗑️  임시 파일 삭제: {txt_file.name}")
        except Exception as e:
            print(f"⚠️  임시 파일 삭제 실패: {str(e)}")
    
    def process_url(self, url: str, converter_type: Optional[str] = None, 
                   keep_txt: bool = False) -> Tuple[bool, Optional[Path]]:
        """
        URL부터 마크다운까지 전체 프로세스 실행
        
        Args:
            url: 처리할 뉴스 기사 URL
            converter_type: 사용할 변환기 타입 (None이면 자동 선택)
            keep_txt: TXT 파일을 보관할지 여부
            
        Returns:
            (성공 여부, 최종 마크다운 파일 경로)
        """
        print(f"\n🎯 전체 프로세스 시작")
        print(f"📍 URL: {url}")
        
        # 1. URL 유효성 검사
        if not self._validate_url(url):
            print("❌ 올바르지 않은 URL 형식입니다.")
            return False, None
        
        # 2. 뉴스 기사 추출
        txt_file = self._extract_article(url)
        if not txt_file:
            return False, None
        
        # 3. 마크다운 변환
        md_file = self._convert_article(txt_file, converter_type)
        if not md_file:
            self._cleanup_temp_file(txt_file)
            return False, None
        
        # 4. 임시 파일 정리 (옵션)
        if not keep_txt:
            self._cleanup_temp_file(txt_file)
        else:
            # extracted_articles로 이동
            extracted_dir = Path('extracted_articles')
            extracted_dir.mkdir(parents=True, exist_ok=True)
            final_txt = extracted_dir / txt_file.name
            txt_file.rename(final_txt)
            print(f"📁 TXT 파일 보관: {final_txt}")
        
        print(f"\n🎉 전체 프로세스 완료!")
        print(f"📄 최종 결과: {md_file}")
        
        return True, md_file
    
    def process_multiple_urls(self, urls: list, converter_type: Optional[str] = None,
                            keep_txt: bool = False) -> list:
        """
        여러 URL을 일괄 처리
        
        Args:
            urls: 처리할 URL 리스트
            converter_type: 사용할 변환기 타입
            keep_txt: TXT 파일을 보관할지 여부
            
        Returns:
            처리 결과 리스트 [(success, md_file), ...]
        """
        results = []
        total = len(urls)
        
        print(f"\n📚 일괄 처리 시작: {total}개 URL")
        
        for i, url in enumerate(urls, 1):
            print(f"\n{'='*50}")
            print(f"📍 진행률: {i}/{total}")
            
            success, md_file = self.process_url(url, converter_type, keep_txt)
            results.append((success, md_file))
        
        # 결과 요약
        success_count = sum(1 for success, _ in results if success)
        print(f"\n📊 일괄 처리 완료!")
        print(f"   성공: {success_count}/{total}")
        print(f"   실패: {total - success_count}/{total}")
        
        return results


def interactive_mode():
    """대화형 모드"""
    print("\n🌐 뉴스 변환 통합 서비스 - 대화형 모드")
    print("=" * 60)
    
    # 변환기 상태 출력
    print_converter_status()
    
    service = NewsConverterService()
    
    while True:
        print(f"\n📋 메뉴:")
        print("1. 단일 URL 변환")
        print("2. 여러 URL 일괄 변환")
        print("3. 변환기 상태 확인")
        print("4. 종료")
        
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == '1':
            # 단일 URL 처리
            url = input("\n🔗 뉴스 기사 URL: ").strip()
            if not url:
                print("❌ URL을 입력해주세요.")
                continue
            
            # 변환기 선택
            converter_type = None
            converter_choice = input("\n🤖 변환기 선택 (Enter=자동선택, a=anthropic, o=openai, l=local): ").strip().lower()
            if converter_choice == 'a':
                converter_type = 'anthropic'
            elif converter_choice == 'o':
                converter_type = 'openai'
            elif converter_choice == 'l':
                converter_type = 'local'
            
            # TXT 파일 보관 여부
            keep_txt = input("\n📁 TXT 파일 보관하시겠습니까? (y/N): ").strip().lower() == 'y'
            
            # 처리 실행
            service.process_url(url, converter_type, keep_txt)
        
        elif choice == '2':
            # 여러 URL 처리
            print("\n🔗 URL을 한 줄씩 입력하세요 (빈 줄로 완료):")
            urls = []
            while True:
                url = input().strip()
                if not url:
                    break
                urls.append(url)
            
            if not urls:
                print("❌ URL이 입력되지 않았습니다.")
                continue
            
            # 변환기 선택
            converter_type = None
            converter_choice = input("\n🤖 변환기 선택 (Enter=자동선택, a=anthropic, o=openai, l=local): ").strip().lower()
            if converter_choice == 'a':
                converter_type = 'anthropic'
            elif converter_choice == 'o':
                converter_type = 'openai'
            elif converter_choice == 'l':
                converter_type = 'local'
            
            # TXT 파일 보관 여부
            keep_txt = input("\n📁 TXT 파일 보관하시겠습니까? (y/N): ").strip().lower() == 'y'
            
            # 처리 실행
            service.process_multiple_urls(urls, converter_type, keep_txt)
        
        elif choice == '3':
            # 상태 확인
            print_converter_status()
        
        elif choice == '4':
            print("👋 종료합니다.")
            break
        
        else:
            print("❌ 올바른 번호를 선택해주세요.")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description="뉴스 변환 통합 서비스 - URL에서 마크다운까지 원스톱",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python news_converter_service.py                                    # 대화형 모드
  python news_converter_service.py "https://example.com/news"         # 단일 URL 변환
  python news_converter_service.py -t anthropic "https://..."         # Anthropic 사용
  python news_converter_service.py --keep-txt "https://..."           # TXT 파일 보관
  python news_converter_service.py --status                           # 변환기 상태 확인
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='변환할 뉴스 기사 URL'
    )
    
    parser.add_argument(
        '-t', '--type',
        choices=['anthropic', 'openai', 'local'],
        help='사용할 변환기 타입 (자동 선택: 기본값)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='converted_articles',
        help='출력 디렉토리 (기본값: converted_articles)'
    )
    
    parser.add_argument(
        '--keep-txt',
        action='store_true',
        help='추출된 TXT 파일을 extracted_articles에 보관'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='변환기 상태만 확인하고 종료'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='대화형 모드 강제 실행'
    )
    
    args = parser.parse_args()
    
    # 상태 확인만 하고 종료
    if args.status:
        print_converter_status()
        return
    
    # 대화형 모드
    if args.interactive or not args.url:
        interactive_mode()
        return
    
    # 직접 변환 모드
    service = NewsConverterService(args.output)
    success, md_file = service.process_url(args.url, args.type, args.keep_txt)
    
    if success:
        print(f"\n🎉 성공적으로 완료되었습니다!")
        print(f"📄 결과 파일: {md_file}")
    else:
        print(f"\n❌ 변환에 실패했습니다.")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1) 