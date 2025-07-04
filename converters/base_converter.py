"""
뉴스 변환기 베이스 클래스

모든 변환기의 공통 기능을 제공하는 추상 베이스 클래스입니다.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dotenv import load_dotenv


class BaseConverter(ABC):
    """뉴스 변환기 베이스 클래스"""
    
    def __init__(self, output_dir: str = 'data/generated'):
        """
        베이스 변환기 초기화
        
        Args:
            output_dir: 출력 디렉토리 경로
        """
        # 환경 변수 로드
        load_dotenv()
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 공통 이모지 매핑
        self.emoji_mapping = {
            'market': '📈',
            'finance': '💰',
            'tech': '🚀',
            'policy': '⚖️',
            'trade': '🤝',
            'energy': '⛽',
            'conflict': '🔥',
            'growth': '🌱',
            'default': '📰'
        }
        
        # 주식 심볼 매핑
        self.company_symbols = {
            'Apple': 'AAPL',
            'Microsoft': 'MSFT',
            'Amazon': 'AMZN',
            'Google': 'GOOGL',
            'Tesla': 'TSLA',
            'Meta': 'META',
            'Netflix': 'NFLX',
            'Nvidia': 'NVDA',
            'Samsung': '005930',
            'SK하이닉스': '000660',
            'LG전자': '066570'
        }
        
    def read_txt_file(self, file_path: str) -> Dict[str, str]:
        """
        TXT 파일을 읽어서 구조화된 데이터로 반환
        
        Args:
            file_path: 입력 파일 경로
            
        Returns:
            title, description, content를 포함한 딕셔너리
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 다양한 형식 지원
        # 형식 1: 기존 형식 (제목: xxx\n====)
        title_match = re.search(r'제목: (.*?)\n={2,}', content)
        meta_match = re.search(r'메타 정보:\ndescription: (.*?)\n-{2,}', content, re.DOTALL)
        content_match = re.search(r'본문:\n(.*?)$', content, re.DOTALL)
        
        # 형식 2: 새로운 형식 (URL:, 제목:, 저자:, 날짜:, 추출일:, ==분리선==, 본문)
        if not title_match:
            # 제목 추출 (URL 다음 줄부터 시작)
            url_match = re.search(r'URL: (.*?)\n', content)
            title_match_new = re.search(r'제목: (.*?)\n', content)
            author_match = re.search(r'저자: (.*?)\n', content)
            date_match = re.search(r'날짜: (.*?)\n', content)
            
            # 본문 추출 (분리선 다음부터 끝까지)
            content_match_new = re.search(r'={10,}\n\n(.*?)$', content, re.DOTALL)
            
            # 실제 제목이 본문에 있는지 확인 (Yahoo Finance 같은 경우)
            if content_match_new:
                content_text = content_match_new.group(1).strip()
                lines = content_text.split('\n')
                # 첫 번째 줄에서 실제 제목 찾기
                real_title = ""
                for line in lines[:5]:  # 처음 5줄만 확인
                    line = line.strip()
                    if line and len(line) > 20 and not any(skip in line.lower() for skip in ['sarah e.', 'fri,', 'min read', 'by taboola']):
                        real_title = line
                        break
                
                return {
                    'title': real_title if real_title else (title_match_new.group(1) if title_match_new else ""),
                    'description': f"저자: {author_match.group(1) if author_match else ''}, 날짜: {date_match.group(1) if date_match else ''}",
                    'content': content_text
                }
        
        # 기본 형식 반환
        return {
            'title': title_match.group(1) if title_match else "",
            'description': meta_match.group(1).strip() if meta_match else "",
            'content': content_match.group(1).strip() if content_match else ""
        }
    
    def clean_content(self, content: str) -> str:
        """
        불필요한 내용 제거
        
        Args:
            content: 원본 내용
            
        Returns:
            정리된 내용
        """
        # 기자 정보 제거
        content = re.sub(r'By\s+[\w\s]+\n', '', content)
        content = re.sub(r'Kevin Buckland.*?\n', '', content, flags=re.IGNORECASE)
        content = re.sub(r'\w+@\w+\.\w+', '', content)  # 이메일 제거
        
        # 메타데이터 제거
        unwanted_patterns = [
            'usd=x', '^spx', 'terms and privacy', 'privacy dashboard',
            'fri,', 'min read', 'in this article', 'reporting by', 'editing by',
            'subscribe', 'newsletter', 'follow us', 'download app'
        ]
        
        lines = content.split('\n')
        filtered_lines = []
        
        for line in lines:
            line = line.strip()
            if (line and len(line) > 20 and 
                not any(pattern in line.lower() for pattern in unwanted_patterns)):
                filtered_lines.append(line)
        
        # 중복 제거
        unique_lines = list(dict.fromkeys(filtered_lines))
        
        return '\n'.join(unique_lines)
    
    def detect_topic(self, text: str) -> str:
        """
        텍스트에서 주요 토픽 감지
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            감지된 토픽
        """
        text_lower = text.lower()
        
        topic_keywords = {
            'market': ['market', 'stock', 'trading', 'index', 'equity', 'shares', '주식', '증시', '시장'],
            'finance': ['bank', 'finance', 'investment', 'fund', 'money', 'dollar', '은행', '투자', '자금'],
            'tech': ['technology', 'tech', 'ai', 'digital', 'software', 'innovation', '기술', '혁신', '소프트웨어'],
            'policy': ['policy', 'regulation', 'law', 'government', 'bill', 'tax', '정책', '규제', '법률'],
            'trade': ['trade', 'tariff', 'export', 'import', 'deal', 'agreement', '무역', '수출', '수입'],
            'energy': ['oil', 'gas', 'energy', 'fuel', 'crude', 'petroleum', '에너지', '석유', '가스']
        }
        
        scores = {topic: 0 for topic in topic_keywords.keys()}
        
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                scores[topic] += text_lower.count(keyword)
        
        if not any(scores.values()):
            return 'default'
        
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def format_stock_symbols(self, text: str) -> str:
        """
        주식 심볼 포맷팅 ($SYMBOL 형식으로 변환)
        
        Args:
            text: 원본 텍스트
            
        Returns:
            포맷팅된 텍스트
        """
        formatted = text
        for company, symbol in self.company_symbols.items():
            if company in formatted:
                formatted = formatted.replace(company, f"{company} ${symbol}")
        
        return formatted
    
    def generate_output_filename(self, input_path: str, suffix: str = "") -> Path:
        """
        출력 파일명 생성
        
        Args:
            input_path: 입력 파일 경로
            suffix: 파일명 접미사
            
        Returns:
            출력 파일 경로
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        input_name = Path(input_path).stem
        
        if suffix:
            filename = f"{input_name}_{suffix}_{timestamp}.md"
        else:
            filename = f"{input_name}_{timestamp}.md"
        
        return self.output_dir / filename
    
    def save_markdown(self, content: str, output_path: Path) -> None:
        """
        마크다운 파일 저장
        
        Args:
            content: 저장할 내용
            output_path: 저장 경로
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Created: {output_path}")
    
    @abstractmethod
    def convert_to_markdown(self, data: Dict[str, str]) -> str:
        """
        데이터를 마크다운으로 변환 (각 변환기에서 구현)
        
        Args:
            data: 구조화된 뉴스 데이터
            
        Returns:
            마크다운 형식의 문자열
        """
        pass
    
    @abstractmethod
    def extract_keywords(self, content: str) -> str:
        """
        키워드 추출 (각 변환기에서 구현)
        
        Args:
            content: 분석할 내용
            
        Returns:
            해시태그 형식의 키워드
        """
        pass
    
    def process_file(self, file_path: str) -> None:
        """
        파일 처리 (공통 워크플로우)
        
        Args:
            file_path: 처리할 파일 경로
        """
        print(f"🔄 Processing: {file_path}")
        
        try:
            # 1. 파일 읽기
            data = self.read_txt_file(file_path)
            
            # 2. 마크다운 변환
            markdown_content = self.convert_to_markdown(data)
            
            # 3. 키워드 추출
            keywords = self.extract_keywords(
                f"{data['title']}\n{data['description']}\n{data['content']}"
            )
            
            # 4. 최종 조합
            final_content = f"{markdown_content}\n\n{keywords}"
            
            # 5. 파일 저장
            output_path = self.generate_output_filename(
                file_path, 
                suffix=self.__class__.__name__.lower().replace('converter', '')
            )
            self.save_markdown(final_content, output_path)
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {str(e)}")
    
    def process_directory(self, directory_path: str) -> None:
        """
        디렉토리 내 모든 TXT 파일 처리
        
        Args:
            directory_path: 처리할 디렉토리 경로
        """
        directory = Path(directory_path)
        txt_files = list(directory.glob('*.txt'))
        
        if not txt_files:
            print(f"❌ No TXT files found in {directory_path}")
            return
        
        print(f"📁 Processing {len(txt_files)} files in {directory_path}")
        
        for txt_file in txt_files:
            self.process_file(str(txt_file)) 