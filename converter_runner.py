#!/usr/bin/env python3
"""
뉴스 변환기 통합 실행 스크립트

다양한 변환기를 통해 뉴스 기사 TXT 파일을 마크다운으로 변환합니다.
API 키 상태에 따라 자동으로 최적의 변환기를 선택합니다.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# 현재 스크립트의 디렉토리 추가
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from converters.factory import create_converter, print_converter_status, get_available_converters


def setup_directories():
    """필요한 디렉토리 생성"""
    directories = [
        'converted_articles',
        'extracted_articles',
        'data/generated'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def find_txt_files(path: str) -> List[Path]:
    """
    TXT 파일 찾기
    
    Args:
        path: 검색할 경로 (파일 또는 디렉토리)
        
    Returns:
        TXT 파일 경로 리스트
    """
    path_obj = Path(path)
    
    if path_obj.is_file():
        if path_obj.suffix.lower() == '.txt':
            return [path_obj]
        else:
            print(f"❌ {path}는 TXT 파일이 아닙니다.")
            return []
    
    elif path_obj.is_dir():
        txt_files = list(path_obj.glob('*.txt'))
        if not txt_files:
            print(f"❌ {path} 디렉토리에서 TXT 파일을 찾을 수 없습니다.")
        return txt_files
    
    else:
        print(f"❌ {path} 경로를 찾을 수 없습니다.")
        return []


def convert_files(input_path: str, converter_type: Optional[str] = None, output_dir: str = 'converted_articles'):
    """
    파일 변환 실행
    
    Args:
        input_path: 입력 파일 또는 디렉토리 경로
        converter_type: 변환기 타입 ('anthropic', 'openai', 'local', None)
        output_dir: 출력 디렉토리
    """
    print(f"🔄 변환 시작: {input_path}")
    
    # TXT 파일 찾기
    txt_files = find_txt_files(input_path)
    if not txt_files:
        return
    
    print(f"📁 발견된 TXT 파일: {len(txt_files)}개")
    
    # 변환기 생성
    try:
        converter = create_converter(converter_type, output_dir)
    except Exception as e:
        print(f"❌ 변환기 생성 실패: {str(e)}")
        return
    
    # 파일별 변환 실행
    success_count = 0
    error_count = 0
    
    for txt_file in txt_files:
        try:
            print(f"\n🔄 처리 중: {txt_file.name}")
            converter.process_file(str(txt_file))
            success_count += 1
        except Exception as e:
            print(f"❌ 변환 실패 ({txt_file.name}): {str(e)}")
            error_count += 1
    
    # 결과 요약
    print(f"\n✅ 변환 완료!")
    print(f"   성공: {success_count}개")
    print(f"   실패: {error_count}개")
    print(f"   출력 디렉토리: {output_dir}")


def interactive_mode():
    """대화형 모드"""
    print("\n🤖 뉴스 변환기 대화형 모드")
    print("=" * 50)
    
    # 변환기 상태 출력
    print_converter_status()
    
    # 입력 경로 선택
    while True:
        print("\n📁 변환할 파일 또는 디렉토리를 선택하세요:")
        print("1. extracted_articles/ (추출된 기사들)")
        print("2. 직접 경로 입력")
        print("3. 종료")
        
        choice = input("\n선택 (1-3): ").strip()
        
        if choice == '1':
            input_path = 'extracted_articles'
        elif choice == '2':
            input_path = input("📂 파일 또는 디렉토리 경로: ").strip()
            if not input_path:
                print("❌ 경로를 입력해주세요.")
                continue
        elif choice == '3':
            print("👋 종료합니다.")
            return
        else:
            print("❌ 올바른 번호를 선택해주세요.")
            continue
        
        # 변환기 타입 선택
        available_converters = get_available_converters()
        valid_converters = [k for k, v in available_converters.items() if v['valid']]
        
        print(f"\n🤖 변환기를 선택하세요:")
        print("0. 자동 선택 (추천)")
        
        for i, converter_type in enumerate(valid_converters, 1):
            info = available_converters[converter_type]
            print(f"{i}. {converter_type.upper()} - {info['description']}")
        
        converter_choice = input(f"\n선택 (0-{len(valid_converters)}): ").strip()
        
        if converter_choice == '0':
            converter_type = None
        elif converter_choice.isdigit() and 1 <= int(converter_choice) <= len(valid_converters):
            converter_type = valid_converters[int(converter_choice) - 1]
        else:
            print("❌ 올바른 번호를 선택해주세요.")
            continue
        
        # 변환 실행
        convert_files(input_path, converter_type)
        
        # 계속 여부 확인
        continue_choice = input("\n계속 변환하시겠습니까? (y/N): ").strip().lower()
        if continue_choice not in ['y', 'yes']:
            print("👋 종료합니다.")
            break


def main():
    """메인 함수"""
    # 디렉토리 설정
    setup_directories()
    
    # 명령행 인자 파싱
    parser = argparse.ArgumentParser(
        description="뉴스 변환기 - TXT 파일을 마크다운으로 변환",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  python converter_runner.py                           # 대화형 모드
  python converter_runner.py extracted_articles/       # 디렉토리 변환
  python converter_runner.py article.txt               # 단일 파일 변환
  python converter_runner.py -t anthropic article.txt  # Anthropic API 사용
  python converter_runner.py -t openai article.txt     # OpenAI API 사용
  python converter_runner.py -t local article.txt      # 로컬 변환기 사용
  python converter_runner.py --status                  # 변환기 상태 확인
        """
    )
    
    parser.add_argument(
        'input_path',
        nargs='?',
        help='변환할 TXT 파일 또는 디렉토리 경로'
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
    if args.interactive or not args.input_path:
        interactive_mode()
        return
    
    # 직접 변환 모드
    convert_files(args.input_path, args.type, args.output)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 사용자에 의해 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1) 