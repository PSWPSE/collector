import os
from datetime import datetime
from pathlib import Path
import re
from collections import Counter
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

class SimpleNewsConverter:
    def __init__(self):
        self.output_dir = Path('converted_articles')
        self.output_dir.mkdir(exist_ok=True)
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('taggers/averaged_perceptron_tagger')
            nltk.data.find('corpora/stopwords')
            nltk.data.find('tokenizers/punkt_tab/english')
        except LookupError:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('stopwords')
            nltk.download('punkt_tab')

        # 이모지 매핑 정의
        self.emoji_mapping = {
            'stock': '📈',
            'market': '📊',
            'finance': '💰',
            'tech': '🚀',
            'policy': '⚖️',
            'conflict': '🔥',
            'growth': '🌱',
            'deal': '🤝',
            'default': '📰'
        }

        # 주요 키워드 매핑
        self.topic_keywords = {
            'stock': ['stock', 'shares', 'market', 'trading', 'nasdaq', 'dow', 's&p'],
            'market': ['market', 'investors', 'trading', 'economy', 'wall street'],
            'finance': ['bank', 'finance', 'investment', 'fund', 'money'],
            'tech': ['technology', 'tech', 'ai', 'digital', 'software', 'innovation'],
            'policy': ['policy', 'regulation', 'law', 'government', 'bill', 'tax'],
            'conflict': ['dispute', 'lawsuit', 'controversy', 'battle', 'fight'],
            'growth': ['growth', 'expansion', 'development', 'increase'],
            'deal': ['deal', 'agreement', 'partnership', 'acquisition', 'merger']
        }

    def read_txt_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse the content
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

    def detect_topic(self, text):
        """텍스트에서 주요 토픽을 감지하여 적절한 이모지 선택"""
        text = text.lower()
        scores = {topic: 0 for topic in self.topic_keywords.keys()}
        
        for topic, keywords in self.topic_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[topic] += 1
        
        if not any(scores.values()):
            return 'default'
        
        return max(scores.items(), key=lambda x: x[1])[0]

    def extract_stock_symbols(self, text):
        """텍스트에서 주식 심볼 추출"""
        # 일반적인 주식 심볼 패턴 ($AAPL, $TSLA 등)
        symbols = re.findall(r'\$([A-Z]{1,5})', text)
        
        # 회사 이름 뒤에 심볼이 없는 경우 추가
        companies = {
            'Apple': 'AAPL',
            'Microsoft': 'MSFT',
            'Amazon': 'AMZN',
            'Google': 'GOOGL',
            'Tesla': 'TSLA',
            'Meta': 'META',
            'Netflix': 'NFLX',
            'Nvidia': 'NVDA'
        }
        
        for company, symbol in companies.items():
            if company in text and symbol not in symbols:
                symbols.append(symbol)
        
        return list(set(symbols))

    def extract_keywords(self, text, num_keywords=5):
        """텍스트에서 주요 키워드 추출"""
        # 텍스트 전처리
        words = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        
        # 불용어 및 특수문자 제거
        words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
        
        # 빈도수 기반 키워드 추출
        word_freq = Counter(words)
        keywords = [word for word, _ in word_freq.most_common(num_keywords)]
        
        return keywords

    def structure_content(self, content):
        """내용을 섹션별로 구조화"""
        paragraphs = content.split('\n\n')
        
        # 섹션 구분
        sections = {
            '▶ 주요 내용:': [],
            '▶ 영향 및 전망:': [],
            '▶ 관련 동향:': []
        }
        
        # 문단 분류
        for i, para in enumerate(paragraphs):
            if i == 0:
                sections['▶ 주요 내용:'].append(para)
            elif '영향' in para.lower() or '전망' in para.lower() or '예상' in para.lower():
                sections['▶ 영향 및 전망:'].append(para)
            else:
                sections['▶ 관련 동향:'].append(para)
        
        # 섹션 텍스트 생성
        structured_content = []
        for section, paras in sections.items():
            if paras:
                structured_content.append(f"\n{section}")
                for para in paras:
                    structured_content.append(f"• {para.strip()}")
        
        return '\n'.join(structured_content)

    def format_stock_mentions(self, text, symbols):
        """주식 심볼 포맷팅"""
        formatted = text
        for symbol in symbols:
            # 회사 이름 찾아서 심볼 추가
            companies = {
                'Apple': 'AAPL',
                'Microsoft': 'MSFT',
                'Amazon': 'AMZN',
                'Google': 'GOOGL',
                'Tesla': 'TSLA',
                'Meta': 'META',
                'Netflix': 'NFLX',
                'Nvidia': 'NVDA'
            }
            
            for company, sym in companies.items():
                if sym == symbol and company in formatted:
                    formatted = formatted.replace(
                        company,
                        f"{company} ${symbol}"
                    )
        
        return formatted

    def convert_to_markdown(self, data):
        """데이터를 마크다운 형식으로 변환"""
        # 토픽 감지 및 이모지 선택
        topic = self.detect_topic(data['title'] + ' ' + data['description'])
        emoji = self.emoji_mapping.get(topic, self.emoji_mapping['default'])
        
        # 주식 심볼 추출
        symbols = self.extract_stock_symbols(data['title'] + ' ' + data['content'])
        
        # 제목 포맷팅
        title = self.format_stock_mentions(data['title'], symbols)
        formatted_title = f"{emoji} {title}"
        
        # 내용 구조화 및 포맷팅
        content = self.format_stock_mentions(data['content'], symbols)
        structured_content = self.structure_content(content)
        
        # 키워드 추출
        keywords = self.extract_keywords(
            data['title'] + ' ' + data['description'] + ' ' + data['content']
        )
        keyword_tags = ' '.join([f"#{keyword}" for keyword in keywords])
        
        # 최종 마크다운 생성
        markdown = f"{formatted_title}\n\n{structured_content}\n\n{keyword_tags}"
        
        return markdown

    def process_file(self, file_path):
        """단일 TXT 파일 처리"""
        print(f"Processing {file_path}...")
        data = self.read_txt_file(file_path)
        markdown_content = self.convert_to_markdown(data)
        
        # 출력 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{Path(file_path).stem}_{timestamp}.md"
        output_path = self.output_dir / output_filename
        
        # 마크다운 저장
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created {output_path}")

    def process_directory(self, directory_path):
        """디렉토리 내 모든 TXT 파일 처리"""
        directory = Path(directory_path)
        for txt_file in directory.glob('*.txt'):
            self.process_file(txt_file)

def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python simple_converter.py <txt_file_or_directory>")
        sys.exit(1)
    
    path = sys.argv[1]
    converter = SimpleNewsConverter()
    
    if os.path.isfile(path):
        converter.process_file(path)
    elif os.path.isdir(path):
        converter.process_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main() 