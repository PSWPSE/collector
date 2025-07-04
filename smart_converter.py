import os
import re
from datetime import datetime
from pathlib import Path
from collections import Counter
from typing import Dict, List

class SmartNewsConverter:
    def __init__(self):
        """실용적인 스마트 뉴스 변환기"""
        self.output_dir = Path('converted_articles')
        self.output_dir.mkdir(exist_ok=True)
        
        # 포괄적인 금융/경제 번역 사전
        self.translation_dict = {
            # 시장 기본 용어
            'Asian stocks': '아시아 주식',
            'stock market': '주식 시장',
            'equity market': '주식 시장',
            'financial market': '금융 시장',
            'capital market': '자본 시장',
            'bond market': '채권 시장',
            'commodity market': '원자재 시장',
            'forex market': '외환 시장',
            'market volatility': '시장 변동성',
            'market sentiment': '시장 심리',
            'market outlook': '시장 전망',
            'trading volume': '거래량',
            'market cap': '시가총액',
            'market share': '시장 점유율',
            
            # 주요 지수
            'Nikkei': '니케이',
            'Hang Seng': '항셍',
            'KOSPI': '코스피',
            'Dow Jones': '다우존스',
            'NASDAQ': '나스닥',
            'S&P 500': 'S&P 500',
            'FTSE': 'FTSE',
            'DAX': 'DAX',
            
            # 통화
            'U.S. dollar': '미국 달러',
            'dollar': '달러',
            'Japanese yen': '일본 엔',
            'yen': '엔',
            'euro': '유로',
            'British pound': '영국 파운드',
            'pound': '파운드',
            'Chinese yuan': '중국 위안',
            'yuan': '위안',
            'Korean won': '한국 원',
            'won': '원',
            
            # 경제 지표
            'GDP': 'GDP',
            'inflation': '인플레이션',
            'interest rate': '금리',
            'unemployment rate': '실업률',
            'employment': '고용',
            'jobs report': '고용 보고서',
            'economic growth': '경제 성장',
            'recession': '경기 침체',
            'recovery': '경기 회복',
            'expansion': '경기 확장',
            
            # 정책/기관
            'Federal Reserve': '연방준비제도',
            'Fed': '연준',
            'central bank': '중앙은행',
            'monetary policy': '통화정책',
            'fiscal policy': '재정정책',
            'government': '정부',
            'administration': '행정부',
            'Congress': '의회',
            'Senate': '상원',
            'House': '하원',
            
            # 기업/비즈니스
            'earnings': '실적',
            'revenue': '매출',
            'profit': '이익',
            'loss': '손실',
            'IPO': 'IPO',
            'merger': '합병',
            'acquisition': '인수',
            'dividend': '배당금',
            'stock split': '주식 분할',
            'buyback': '자사주 매입',
            
            # 방향성/변화
            'rose': '상승했다',
            'fell': '하락했다',
            'gained': '상승했다',
            'declined': '하락했다',
            'increased': '증가했다',
            'decreased': '감소했다',
            'surged': '급등했다',
            'plunged': '급락했다',
            'climbed': '올랐다',
            'dropped': '떨어졌다',
            'jumped': '급등했다',
            'slumped': '급락했다',
            'edged up': '소폭 상승했다',
            'edged down': '소폭 하락했다',
            'rallied': '반등했다',
            'tumbled': '급락했다',
            
            # 정도 표현
            'significantly': '크게',
            'substantially': '상당히',
            'moderately': '적당히',
            'slightly': '약간',
            'marginally': '미미하게',
            'sharply': '급격히',
            'dramatically': '극적으로',
            
            # 시간 표현
            'overnight': '전날 밤',
            'premarket': '장전',
            'after hours': '장후',
            'trading session': '거래 세션',
            'trading day': '거래일',
            'business day': '영업일',
            'weekend': '주말',
            'weekday': '평일',
            
            # 기타 중요 용어
            'investors': '투자자들',
            'traders': '거래자들',
            'analysts': '분석가들',
            'experts': '전문가들',
            'economists': '경제학자들',
            'strategists': '전략가들',
            'portfolio': '포트폴리오',
            'hedge fund': '헤지펀드',
            'mutual fund': '뮤추얼펀드',
            'pension fund': '연기금',
            'institutional investor': '기관투자자',
            'retail investor': '개인투자자'
        }
        
        # 이모지 매핑
        self.emoji_mapping = {
            'market': '📈',
            'finance': '💰',
            'tech': '🚀',
            'policy': '⚖️',
            'trade': '🤝',
            'energy': '⛽',
            'default': '📰'
        }

    def smart_translate(self, text: str) -> str:
        """스마트 번역 (문맥 고려)"""
        # 숫자와 특수 기호 보존
        text = re.sub(r'(\d+\.?\d*%)', r'PERCENT_\1', text)
        text = re.sub(r'(\$\d+\.?\d*)', r'DOLLAR_\1', text)
        text = re.sub(r'(\d+\.?\d*)', r'NUMBER_\1', text)
        
        # 고유명사 보존 (대문자로 시작하는 단어)
        proper_nouns = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
        for i, noun in enumerate(proper_nouns):
            text = text.replace(noun, f'PROPER_{i}')
        
        # 번역 적용
        translated = text
        for en_term, ko_term in self.translation_dict.items():
            translated = re.sub(
                r'\b' + re.escape(en_term) + r'\b',
                ko_term,
                translated,
                flags=re.IGNORECASE
            )
        
        # 복원
        for i, noun in enumerate(proper_nouns):
            translated = translated.replace(f'PROPER_{i}', noun)
        
        translated = re.sub(r'NUMBER_(\d+\.?\d*)', r'\1', translated)
        translated = re.sub(r'DOLLAR_(\$\d+\.?\d*)', r'\1', translated)
        translated = re.sub(r'PERCENT_(\d+\.?\d*%)', r'\1', translated)
        
        return translated

    def clean_and_structure(self, content: str) -> Dict[str, List[str]]:
        """내용 정리 및 구조화"""
        # 불필요한 내용 제거
        lines = content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # 기자 정보, 메타데이터, 중복 제거
            if (line and len(line) > 20 and 
                not any(skip in line.lower() for skip in [
                    'kevin buckland', 'by ', 'reporting by', 'editing by',
                    'usd=x', '^spx', 'fri,', 'min read', 'terms and privacy',
                    'privacy dashboard', 'in this article'
                ])):
                cleaned_lines.append(line)
        
        # 중복 제거
        unique_lines = list(dict.fromkeys(cleaned_lines))
        
        # 카테고리별 분류
        categories = {
            'market_status': [],
            'economic_data': [],
            'policy_trade': [],
            'outlook': []
        }
        
        for line in unique_lines:
            line_lower = line.lower()
            
            if any(keyword in line_lower for keyword in [
                'market', 'stock', 'index', 'trading', 'nikkei', 'kospi', 'hang seng'
            ]):
                categories['market_status'].append(line)
            elif any(keyword in line_lower for keyword in [
                'jobs', 'employment', 'economic', 'data', 'gdp', 'inflation'
            ]):
                categories['economic_data'].append(line)
            elif any(keyword in line_lower for keyword in [
                'trump', 'president', 'trade', 'tariff', 'deal', 'policy'
            ]):
                categories['policy_trade'].append(line)
            elif any(keyword in line_lower for keyword in [
                'expect', 'forecast', 'outlook', 'ahead', 'future'
            ]):
                categories['outlook'].append(line)
            else:
                # 가장 적절한 카테고리에 추가
                if len(categories['market_status']) <= len(categories['policy_trade']):
                    categories['market_status'].append(line)
                else:
                    categories['policy_trade'].append(line)
        
        return categories

    def generate_smart_title(self, content: str) -> str:
        """스마트 제목 생성"""
        content_lower = content.lower()
        
        # 핵심 키워드 감지
        keywords = []
        
        if 'asian' in content_lower and any(word in content_lower for word in ['stock', 'market']):
            keywords.append('아시아 주식시장')
        
        if any(word in content_lower for word in ['trump', 'trade', 'tariff']):
            keywords.append('무역정책')
        
        if any(word in content_lower for word in ['dollar', 'currency', 'exchange']):
            keywords.append('달러')
        
        if 'deadline' in content_lower:
            keywords.append('마감일')
        
        # 제목 구성
        if keywords:
            if len(keywords) == 1:
                title = f"📈 {keywords[0]} 동향"
            else:
                title = f"📈 {keywords[0]}, {keywords[1]} 관련 소식"
        else:
            title = "📰 경제 뉴스 분석"
        
        return title

    def extract_smart_keywords(self, content: str) -> str:
        """스마트 키워드 추출"""
        # 한국어 키워드 우선 추출
        korean_terms = []
        
        for en_term, ko_term in self.translation_dict.items():
            if en_term.lower() in content.lower():
                korean_terms.append(ko_term.replace(' ', ''))
        
        # 중복 제거 및 상위 5개 선택
        unique_terms = list(dict.fromkeys(korean_terms))[:5]
        
        # 해시태그 형식으로 변환
        hashtags = [f"#{term}" for term in unique_terms]
        
        return ' '.join(hashtags) if hashtags else '#경제뉴스 #시장동향'

    def read_txt_file(self, file_path: str) -> Dict[str, str]:
        """TXT 파일 읽기"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        title_match = re.search(r'제목: (.*?)\n={2,}', content)
        meta_match = re.search(r'메타 정보:\ndescription: (.*?)\n-{2,}', content, re.DOTALL)
        content_match = re.search(r'본문:\n(.*?)$', content, re.DOTALL)
        
        return {
            'title': title_match.group(1) if title_match else "",
            'description': meta_match.group(1).strip() if meta_match else "",
            'content': content_match.group(1).strip() if content_match else ""
        }

    def convert_to_markdown(self, data: Dict[str, str]) -> str:
        """마크다운 변환"""
        full_content = f"{data['title']} {data['description']} {data['content']}"
        
        # 제목 생성
        title = self.generate_smart_title(full_content)
        
        # 내용 구조화
        structured = self.clean_and_structure(data['content'])
        
        # 마크다운 구성
        markdown_parts = [title, ""]
        
        # 시장 현황
        if structured['market_status']:
            markdown_parts.append("▶ 시장 현황:")
            for item in structured['market_status'][:3]:
                translated = self.smart_translate(item)
                markdown_parts.append(f"• {translated}")
            markdown_parts.append("")
        
        # 경제 지표
        if structured['economic_data']:
            markdown_parts.append("▶ 경제 지표:")
            for item in structured['economic_data'][:2]:
                translated = self.smart_translate(item)
                markdown_parts.append(f"• {translated}")
            markdown_parts.append("")
        
        # 정책/무역
        if structured['policy_trade']:
            markdown_parts.append("▶ 정책 및 무역:")
            for item in structured['policy_trade'][:3]:
                translated = self.smart_translate(item)
                markdown_parts.append(f"• {translated}")
            markdown_parts.append("")
        
        # 전망
        if structured['outlook']:
            markdown_parts.append("▶ 향후 전망:")
            for item in structured['outlook'][:2]:
                translated = self.smart_translate(item)
                markdown_parts.append(f"• {translated}")
            markdown_parts.append("")
        
        # 키워드
        keywords = self.extract_smart_keywords(full_content)
        markdown_parts.extend(["", keywords])
        
        return '\n'.join(markdown_parts)

    def process_file(self, file_path: str) -> None:
        """파일 처리"""
        print(f"Processing {file_path} with Smart Converter...")
        
        data = self.read_txt_file(file_path)
        markdown_content = self.convert_to_markdown(data)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{Path(file_path).stem}_smart_{timestamp}.md"
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created {output_path}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python smart_converter.py <txt_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    converter = SmartNewsConverter()
    
    if os.path.isfile(file_path):
        converter.process_file(file_path)
    else:
        print(f"Error: {file_path} is not a valid file")
        sys.exit(1)

if __name__ == '__main__':
    main() 