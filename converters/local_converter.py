"""
로컬 규칙 기반 뉴스 변환기

API 없이 로컬에서 작동하는 변환기로, 규칙 기반 알고리즘을 사용하여 
뉴스 기사를 마크다운으로 변환합니다.
"""

import re
import math
from typing import Dict, List, Tuple
from collections import Counter
from .base_converter import BaseConverter


class LocalConverter(BaseConverter):
    """로컬 규칙 기반 변환기"""
    
    def __init__(self, output_dir: str = 'data/generated'):
        """
        로컬 변환기 초기화
        
        Args:
            output_dir: 출력 디렉토리 경로
        """
        super().__init__(output_dir)
        print("⚡ Using Local Rule-based Converter")
        
        # 한국어 불용어 (조사, 어미 등)
        self.stopwords = {
            '이', '는', '가', '을', '를', '의', '에', '와', '과', '으로', '로', '에서', '으로부터',
            '이다', '있다', '없다', '되다', '하다', '한다', '했다', '할', '것', '수', '및', '그리고',
            '또한', '하지만', '그러나', '따라서', '이에', '이와', '같이', '때문에', '위해', '통해',
            '관련', '대한', '대해', '위한', '아래', '위', '중', '내', '외', '간', '전', '후', '동안',
            '그', '이', '저', '그것', '이것', '저것', '여기', '거기', '저기', '이렇게', '그렇게',
            '더', '가장', '매우', '정말', '너무', '조금', '많이', '약간', '잠깐', '다시', '아직',
            '벌써', '이미', '지금', '오늘', '내일', '어제', '요즘', '최근', '현재', '과거', '미래'
        }
        
        # 문단 분리 패턴
        self.paragraph_patterns = [
            r'하지만',
            r'그러나', 
            r'따라서',
            r'이에 따라',
            r'한편',
            r'또한',
            r'그런데',
            r'이와 함께',
            r'이를 통해',
            r'이번에',
            r'최근',
            r'현재',
            r'과거',
            r'미래'
        ]
        
        # 키워드 매핑 사전
        self.keyword_mapping = {
            # 경제/금융
            'economy': '경제', 'finance': '금융', 'investment': '투자', 'stock': '주식',
            'market': '시장', 'bank': '은행', 'trading': '거래', 'fund': '펀드',
            'asset': '자산', 'profit': '이익', 'revenue': '수익', 'cost': '비용',
            'price': '가격', 'value': '가치', 'growth': '성장', 'decline': '하락',
            
            # 기술/IT
            'technology': '기술', 'ai': '인공지능', 'artificial intelligence': '인공지능',
            'machine learning': '머신러닝', 'blockchain': '블록체인', 'cryptocurrency': '암호화폐',
            'bitcoin': '비트코인', 'ethereum': '이더리움', 'software': '소프트웨어',
            'hardware': '하드웨어', 'digital': '디지털', 'cloud': '클라우드',
            'internet': '인터넷', 'online': '온라인', 'mobile': '모바일',
            
            # 정치/정책
            'policy': '정책', 'government': '정부', 'politics': '정치', 'law': '법률',
            'regulation': '규제', 'bill': '법안', 'congress': '의회', 'senate': '상원',
            'house': '하원', 'president': '대통령', 'minister': '장관', 'election': '선거',
            
            # 비즈니스
            'business': '비즈니스', 'company': '회사', 'corporation': '기업', 'startup': '스타트업',
            'ceo': '최고경영자', 'management': '경영진', 'merger': '합병', 'acquisition': '인수',
            'partnership': '파트너십', 'contract': '계약', 'deal': '거래', 'agreement': '협정',
            
            # 에너지/환경
            'energy': '에너지', 'oil': '석유', 'gas': '가스', 'renewable': '재생에너지',
            'environment': '환경', 'climate': '기후', 'carbon': '탄소', 'emission': '배출',
            'green': '친환경', 'sustainability': '지속가능성'
        }
    
    def extract_keywords(self, content: str) -> str:
        """
        규칙 기반 키워드 추출
        
        Args:
            content: 분석할 내용
            
        Returns:
            해시태그 형식의 키워드
        """
        # 텍스트 전처리
        content = content.lower()
        content = re.sub(r'[^\w\s가-힣]', ' ', content)
        
        # 단어 분리
        words = content.split()
        
        # 불용어 제거 및 길이 필터링
        filtered_words = [
            word for word in words 
            if word not in self.stopwords and len(word) > 1
        ]
        
        # 단어 빈도 계산
        word_freq = Counter(filtered_words)
        
        # 영어 키워드 한국어 변환
        korean_keywords = []
        for word, freq in word_freq.items():
            if word in self.keyword_mapping:
                korean_keywords.append(self.keyword_mapping[word])
            elif freq > 1:  # 2회 이상 언급된 단어만
                korean_keywords.append(word)
        
        # 중복 제거 및 상위 키워드 선택
        unique_keywords = list(dict.fromkeys(korean_keywords))[:7]
        
        # 주식 심볼 감지
        stock_symbols = re.findall(r'\$[A-Z]{1,5}', content.upper())
        if stock_symbols:
            unique_keywords.extend([symbol.replace('$', '') for symbol in stock_symbols[:2]])
        
        # 해시태그 형식으로 변환
        hashtags = [f"#{keyword}" for keyword in unique_keywords[:7]]
        
        return ' '.join(hashtags)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        텍스트를 문장으로 분리
        
        Args:
            text: 분리할 텍스트
            
        Returns:
            문장 리스트
        """
        # 문장 구분자로 분리
        sentences = re.split(r'[.!?。]+', text)
        
        # 빈 문장 제거 및 정리
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # 최소 길이 필터
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _calculate_sentence_score(self, sentence: str, word_freq: Counter) -> float:
        """
        문장 중요도 점수 계산
        
        Args:
            sentence: 점수를 계산할 문장
            word_freq: 단어 빈도 카운터
            
        Returns:
            문장 점수
        """
        words = sentence.lower().split()
        score = 0
        
        for word in words:
            if word in word_freq:
                score += word_freq[word]
        
        # 문장 길이로 정규화
        if len(words) > 0:
            score = score / len(words)
        
        return score
    
    def _extract_key_sentences(self, content: str, num_sentences: int = 5) -> List[str]:
        """
        핵심 문장 추출
        
        Args:
            content: 분석할 내용
            num_sentences: 추출할 문장 수
            
        Returns:
            핵심 문장 리스트
        """
        sentences = self._split_into_sentences(content)
        
        if len(sentences) <= num_sentences:
            return sentences
        
        # 단어 빈도 계산
        all_words = content.lower().split()
        word_freq = Counter([
            word for word in all_words 
            if word not in self.stopwords and len(word) > 1
        ])
        
        # 각 문장 점수 계산
        sentence_scores = []
        for i, sentence in enumerate(sentences):
            score = self._calculate_sentence_score(sentence, word_freq)
            sentence_scores.append((score, i, sentence))
        
        # 점수 순으로 정렬하여 상위 문장 선택
        sentence_scores.sort(key=lambda x: x[0], reverse=True)
        
        # 상위 문장들을 원본 순서로 재정렬
        selected_sentences = sentence_scores[:num_sentences]
        selected_sentences.sort(key=lambda x: x[1])
        
        return [sentence for _, _, sentence in selected_sentences]
    
    def _create_sections(self, content: str) -> List[Tuple[str, List[str]]]:
        """
        내용을 섹션으로 구분
        
        Args:
            content: 분석할 내용
            
        Returns:
            (섹션명, 문장리스트) 튜플 리스트
        """
        key_sentences = self._extract_key_sentences(content, 8)
        
        if len(key_sentences) <= 3:
            return [("주요 내용", key_sentences)]
        
        # 문장들을 주제별로 그룹화
        sections = []
        current_section = []
        
        for i, sentence in enumerate(key_sentences):
            current_section.append(sentence)
            
            # 3-4개 문장마다 새 섹션 생성
            if len(current_section) >= 3 and i < len(key_sentences) - 1:
                section_name = self._generate_section_name(current_section)
                sections.append((section_name, current_section.copy()))
                current_section = []
        
        # 남은 문장들 처리
        if current_section:
            section_name = self._generate_section_name(current_section)
            sections.append((section_name, current_section))
        
        return sections
    
    def _generate_section_name(self, sentences: List[str]) -> str:
        """
        문장들을 기반으로 섹션명 생성
        
        Args:
            sentences: 섹션의 문장들
            
        Returns:
            섹션명
        """
        # 핵심 단어 추출
        all_text = ' '.join(sentences).lower()
        words = all_text.split()
        
        # 빈도 기반 키워드 추출
        word_freq = Counter([
            word for word in words 
            if word not in self.stopwords and len(word) > 1
        ])
        
        if not word_freq:
            return "주요 내용"
        
        # 가장 빈번한 단어 기반 섹션명 생성
        top_word = word_freq.most_common(1)[0][0]
        
        # 섹션명 매핑
        section_mapping = {
            '시장': '시장 동향',
            '주식': '주식 현황',
            '투자': '투자 동향',
            '경제': '경제 상황',
            '정책': '정책 변화',
            '기술': '기술 발전',
            '회사': '기업 동향',
            '성장': '성장 전망',
            '변화': '변화 현황',
            '발표': '발표 내용',
            '계획': '향후 계획',
            '결과': '주요 결과',
            '영향': '영향 분석',
            '전망': '미래 전망'
        }
        
        # 매핑에서 찾기
        for key, value in section_mapping.items():
            if key in all_text:
                return value
        
        return "주요 내용"
    
    def convert_to_markdown(self, data: Dict[str, str]) -> str:
        """
        규칙 기반 마크다운 변환
        
        Args:
            data: 구조화된 뉴스 데이터
            
        Returns:
            마크다운 형식의 문자열
        """
        # 내용 정제
        content = self.clean_content(data['content'])
        
        # 토픽 감지 및 이모지 선택
        topic = self.detect_topic(f"{data['title']} {data['description']} {content}")
        emoji = self.emoji_mapping.get(topic, '📰')
        
        # 제목 생성 (원본 제목 활용)
        title = data['title'].strip()
        if not title:
            title = data['description'][:50] + "..."
        
        formatted_title = f"{emoji} {title}"
        
        # 섹션 생성
        sections = self._create_sections(content)
        
        # 마크다운 구성
        markdown_lines = [formatted_title, ""]
        
        for section_name, sentences in sections:
            markdown_lines.append(f"▶ {section_name}:")
            
            for sentence in sentences:
                # 문장 정리
                sentence = sentence.strip()
                if sentence:
                    # 주식 심볼 포맷팅
                    sentence = self.format_stock_symbols(sentence)
                    markdown_lines.append(f"• {sentence}")
            
            markdown_lines.append("")  # 섹션 간 빈 줄
        
        # 마지막 빈 줄 제거
        while markdown_lines and markdown_lines[-1] == "":
            markdown_lines.pop()
        
        return '\n'.join(markdown_lines) 