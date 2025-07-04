import os
import re
from datetime import datetime
from pathlib import Path
from collections import Counter
import requests
import json
from typing import Dict, List, Optional

class EnhancedNewsConverter:
    def __init__(self, use_online_translation=True):
        """
        개선된 뉴스 변환기
        
        Args:
            use_online_translation: 온라인 번역 사용 여부 (False시 완전 오프라인)
        """
        self.use_online_translation = use_online_translation
        self.output_dir = Path('converted_articles')
        self.output_dir.mkdir(exist_ok=True)
        
        # 이모지 매핑 (토픽별)
        self.emoji_mapping = {
            'market': '📈',
            'finance': '💰',
            'tech': '🚀',
            'policy': '⚖️',
            'trade': '🤝',
            'conflict': '🔥',
            'growth': '🌱',
            'default': '📰'
        }
        
        # 토픽 키워드 (영한 매핑)
        self.topic_keywords = {
            'market': {
                'en': ['market', 'stock', 'trading', 'nasdaq', 'dow', 'index', 'equity'],
                'ko': ['시장', '주식', '거래', '지수']
            },
            'finance': {
                'en': ['bank', 'finance', 'investment', 'fund', 'money', 'dollar'],
                'ko': ['은행', '금융', '투자', '펀드', '달러']
            },
            'tech': {
                'en': ['technology', 'tech', 'ai', 'digital', 'software'],
                'ko': ['기술', '디지털', '소프트웨어']
            },
            'policy': {
                'en': ['policy', 'regulation', 'law', 'government', 'bill'],
                'ko': ['정책', '규제', '법률', '정부']
            },
            'trade': {
                'en': ['trade', 'tariff', 'export', 'import', 'deal'],
                'ko': ['무역', '관세', '수출', '수입', '협상']
            }
        }
        
        # 기본 번역 사전 (자주 사용되는 금융/경제 용어)
        self.translation_dict = {
            # 시장 관련
            'Asian stocks': '아시아 주식',
            'stock market': '주식 시장',
            'equity market': '주식 시장',
            'Wall Street': '월가',
            'market': '시장',
            'trading': '거래',
            'investors': '투자자들',
            'shares': '주식',
            
            # 지수 관련
            'Nikkei': '니케이',
            'Hang Seng': '항셍',
            'KOSPI': '코스피',
            'Dow': '다우',
            'S&P': 'S&P',
            'NASDAQ': '나스닥',
            
            # 경제 지표
            'GDP': 'GDP',
            'inflation': '인플레이션',
            'interest rate': '금리',
            'Federal Reserve': '연방준비제도',
            'jobs report': '고용 보고서',
            'unemployment': '실업률',
            
            # 통화
            'dollar': '달러',
            'yen': '엔',
            'euro': '유로',
            'yuan': '위안',
            'won': '원',
            
            # 정책/정치
            'President': '대통령',
            'government': '정부',
            'policy': '정책',
            'regulation': '규제',
            'tariff': '관세',
            'trade deal': '무역 협정',
            
            # 기업/산업
            'technology': '기술',
            'artificial intelligence': '인공지능',
            'AI': 'AI',
            'startup': '스타트업',
            'IPO': 'IPO',
            
            # 방향성
            'rose': '상승',
            'fell': '하락',
            'gained': '상승',
            'declined': '하락',
            'increased': '증가',
            'decreased': '감소',
            'up': '상승',
            'down': '하락',
            'higher': '상승',
            'lower': '하락'
        }
        
        # 섹션 템플릿
        self.section_templates = {
            'market_status': '▶ 시장 현황:',
            'economic_data': '▶ 경제 지표:',
            'policy_news': '▶ 정책 동향:',
            'trade_news': '▶ 무역 협상:',
            'company_news': '▶ 기업 동향:',
            'outlook': '▶ 향후 전망:'
        }

    def detect_topic(self, text: str) -> str:
        """텍스트에서 주요 토픽 감지"""
        text_lower = text.lower()
        scores = {topic: 0 for topic in self.topic_keywords.keys()}
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords['en']:
                scores[topic] += text_lower.count(keyword)
        
        if not any(scores.values()):
            return 'default'
        
        return max(scores.items(), key=lambda x: x[1])[0]

    def translate_text_local(self, text: str) -> str:
        """로컬 번역 사전을 사용한 기본 번역"""
        translated = text
        
        # 기본 번역 사전 적용
        for en_term, ko_term in self.translation_dict.items():
            # 대소문자 구분 없이 치환
            translated = re.sub(
                re.escape(en_term), 
                ko_term, 
                translated, 
                flags=re.IGNORECASE
            )
        
        return translated

    def translate_text_online(self, text: str) -> str:
        """온라인 번역 서비스 사용 (Google Translate 무료 API)"""
        if not self.use_online_translation:
            return self.translate_text_local(text)
        
        try:
            # Google Translate 무료 API 사용
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': 'en',
                'tl': 'ko',
                'dt': 't',
                'q': text
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                result = response.json()
                translated = ''.join([item[0] for item in result[0] if item[0]])
                return translated
            else:
                # 온라인 번역 실패시 로컬 번역으로 폴백
                return self.translate_text_local(text)
                
        except Exception as e:
            print(f"온라인 번역 실패, 로컬 번역 사용: {e}")
            return self.translate_text_local(text)

    def clean_content(self, content: str) -> str:
        """불필요한 내용 제거"""
        # 기자 정보 제거
        content = re.sub(r'By\s+[\w\s]+\n', '', content)
        content = re.sub(r'Kevin Buckland.*?\n', '', content)
        content = re.sub(r'\w+@\w+\.\w+', '', content)  # 이메일 제거
        
        # 중복 라인 제거
        lines = content.split('\n')
        unique_lines = []
        seen = set()
        
        for line in lines:
            line = line.strip()
            if line and line not in seen and len(line) > 10:
                unique_lines.append(line)
                seen.add(line)
        
        # 메타데이터 제거
        filtered_lines = []
        for line in unique_lines:
            if not any(skip in line.lower() for skip in [
                'usd=x', '^spx', 'terms and privacy', 'privacy dashboard',
                'fri,', 'min read', 'in this article'
            ]):
                filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)

    def categorize_sentences(self, sentences: List[str]) -> Dict[str, List[str]]:
        """문장을 카테고리별로 분류"""
        categories = {
            'market_status': [],
            'economic_data': [],
            'policy_news': [],
            'trade_news': [],
            'company_news': [],
            'outlook': []
        }
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # 시장 현황
            if any(keyword in sentence_lower for keyword in [
                'market', 'stock', 'index', 'trading', 'nikkei', 'kospi', 'hang seng'
            ]):
                categories['market_status'].append(sentence)
            
            # 경제 지표
            elif any(keyword in sentence_lower for keyword in [
                'jobs', 'employment', 'gdp', 'inflation', 'data', 'report'
            ]):
                categories['economic_data'].append(sentence)
            
            # 정책 뉴스
            elif any(keyword in sentence_lower for keyword in [
                'president', 'government', 'policy', 'regulation', 'bill'
            ]):
                categories['policy_news'].append(sentence)
            
            # 무역 뉴스
            elif any(keyword in sentence_lower for keyword in [
                'trade', 'tariff', 'deal', 'agreement', 'negotiation'
            ]):
                categories['trade_news'].append(sentence)
            
            # 향후 전망
            elif any(keyword in sentence_lower for keyword in [
                'expect', 'forecast', 'outlook', 'future', 'ahead'
            ]):
                categories['outlook'].append(sentence)
            
            # 기타는 회사 뉴스로
            else:
                categories['company_news'].append(sentence)
        
        return categories

    def generate_title(self, content: str, topic: str) -> str:
        """내용 기반 제목 생성"""
        # 핵심 키워드 추출
        key_phrases = []
        
        if 'asian' in content.lower() and 'stock' in content.lower():
            key_phrases.append('아시아 주식')
        
        if 'trade' in content.lower() and 'deal' in content.lower():
            key_phrases.append('무역 협상')
        
        if 'tariff' in content.lower():
            key_phrases.append('관세')
        
        if 'trump' in content.lower():
            key_phrases.append('트럼프')
        
        # 제목 구성
        emoji = self.emoji_mapping.get(topic, self.emoji_mapping['default'])
        
        if key_phrases:
            title = f"{emoji} {', '.join(key_phrases[:2])} 관련 동향"
        else:
            title = f"{emoji} 시장 동향 분석"
        
        return title

    def extract_keywords_smart(self, content: str) -> str:
        """스마트 키워드 추출"""
        # 영어 키워드 추출
        words = re.findall(r'\b[a-zA-Z]{3,}\b', content.lower())
        
        # 불용어 제거
        stopwords = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
        words = [w for w in words if w not in stopwords and len(w) > 3]
        
        # 빈도수 기반 키워드 선정
        word_freq = Counter(words)
        top_words = [word for word, _ in word_freq.most_common(5)]
        
        # 한국어로 번역된 키워드 추가
        korean_keywords = []
        for word in top_words:
            if word in self.translation_dict:
                korean_keywords.append(self.translation_dict[word])
            else:
                korean_keywords.append(word)
        
        # 해시태그 형식으로 반환
        hashtags = [f"#{keyword.replace(' ', '')}" for keyword in korean_keywords]
        return ' '.join(hashtags)

    def read_txt_file(self, file_path: str) -> Dict[str, str]:
        """TXT 파일 읽기"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파싱
        title_match = re.search(r'제목: (.*?)\n={2,}', content)
        meta_match = re.search(r'메타 정보:\ndescription: (.*?)\n-{2,}', content, re.DOTALL)
        content_match = re.search(r'본문:\n(.*?)$', content, re.DOTALL)
        
        title = title_match.group(1) if title_match else ""
        description = meta_match.group(1).strip() if meta_match else ""
        main_content = content_match.group(1).strip() if content_match else ""
        
        return {
            'title': title,
            'description': description,
            'content': main_content
        }

    def convert_to_markdown(self, data: Dict[str, str]) -> str:
        """마크다운 변환"""
        full_content = f"{data['title']} {data['description']} {data['content']}"
        
        # 1. 토픽 감지
        topic = self.detect_topic(full_content)
        
        # 2. 제목 생성
        title = self.generate_title(full_content, topic)
        
        # 3. 본문 정리
        cleaned_content = self.clean_content(data['content'])
        
        # 4. 문장 분리 및 번역
        sentences = [s.strip() for s in cleaned_content.split('.') if s.strip() and len(s.strip()) > 20]
        
        # 5. 문장 카테고리 분류
        categorized = self.categorize_sentences(sentences)
        
        # 6. 마크다운 구성
        markdown_parts = [title, ""]
        
        for category, template in self.section_templates.items():
            if categorized[category]:
                markdown_parts.append(template)
                for sentence in categorized[category][:3]:  # 각 섹션당 최대 3개 문장
                    # 번역 적용
                    if self.use_online_translation:
                        translated = self.translate_text_online(sentence)
                    else:
                        translated = self.translate_text_local(sentence)
                    markdown_parts.append(f"• {translated}")
                markdown_parts.append("")
        
        # 7. 키워드 추가
        keywords = self.extract_keywords_smart(full_content)
        markdown_parts.extend(["", keywords])
        
        return '\n'.join(markdown_parts)

    def process_file(self, file_path: str) -> None:
        """파일 처리"""
        print(f"Processing {file_path} with Enhanced Converter...")
        
        # 파일 읽기
        data = self.read_txt_file(file_path)
        
        # 마크다운 변환
        markdown_content = self.convert_to_markdown(data)
        
        # 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{Path(file_path).stem}_enhanced_{timestamp}.md"
        output_path = self.output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created {output_path}")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python enhanced_converter.py <txt_file> [--offline]")
        print("  --offline: 완전 오프라인 모드 (온라인 번역 사용 안함)")
        sys.exit(1)
    
    file_path = sys.argv[1]
    offline_mode = '--offline' in sys.argv
    
    converter = EnhancedNewsConverter(use_online_translation=not offline_mode)
    
    if os.path.isfile(file_path):
        converter.process_file(file_path)
    else:
        print(f"Error: {file_path} is not a valid file")
        sys.exit(1)

if __name__ == '__main__':
    main() 