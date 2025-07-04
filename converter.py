import os
from datetime import datetime
from pathlib import Path
import anthropic
from openai import OpenAI
from dotenv import load_dotenv
import re

class NewsConverter:
    def __init__(self, api_provider='anthropic'):
        load_dotenv()
        self.api_provider = api_provider.lower()
        self.anthropic_client = None
        self.openai_client = None
        
        if self.api_provider == 'anthropic':
            self.anthropic_client = anthropic.Anthropic(
                api_key=os.getenv('ANTHROPIC_API_KEY')
            )
        if self.api_provider == 'openai' or os.getenv('OPENAI_API_KEY'):
            self.openai_client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY')
            )
        self.output_dir = Path('converted_articles')
        self.output_dir.mkdir(exist_ok=True)

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

    def clean_response(self, response):
        """Clean the API response text"""
        # Handle different API response formats
        text = str(response)
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('TextBlock(citations=None, text=', '')
        text = text.replace(', type=\'text\')', '')
        text = text.strip('"\'')
        text = text.lstrip('\n')
        text = text.replace('\\n', '\n')
        return text.strip()

    def call_api(self, prompt, max_tokens=2000, temperature=0):
        """Call the appropriate API based on provider, fallback to OpenAI if Anthropic fails"""
        # Try Anthropic first if selected
        if self.api_provider == 'anthropic' and self.anthropic_client:
            try:
                message = self.anthropic_client.messages.create(
                    model="claude-3-opus-20240229",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                print("[INFO] Used Anthropic API.")
                return message.content[0]
            except Exception as e:
                print(f"[WARN] Anthropic API failed: {e}\nFalling back to OpenAI API...")
                if not self.openai_client:
                    raise RuntimeError("OpenAI API key not set. Cannot fallback.")
                # Fallback to OpenAI
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                print("[INFO] Used OpenAI API (fallback).")
                return response.choices[0].message.content
        elif self.api_provider == 'openai' and self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            print("[INFO] Used OpenAI API.")
            return response.choices[0].message.content
        else:
            raise RuntimeError("No valid API client available.")

    def extract_keywords(self, content):
        """Extract keywords from content using selected API"""
        prompt = f"""당신은 뉴스 기사에서 핵심 키워드를 추출하는 전문가입니다.
        다음 기사에서 5-7개의 관련 키워드를 추출하여 해시태그 형식으로 반환해주세요.
        
        규칙:
        1. 해시태그는 한글 스타일로 작성 (#키워드)
        2. 각 해시태그는 공백으로 구분
        3. 주식 종목이 언급된 경우 반드시 포함
        4. 가장 중요한 주제어 위주로 선정
        5. 다른 텍스트나 설명 없이 해시태그만 반환
        
        예시 형식:
        #키워드1 #키워드2 #키워드3 #키워드4 #키워드5
        
        Article: {content}"""
        
        response = self.call_api(prompt, max_tokens=300)
        return self.clean_response(response)

    def generate_markdown_content(self, content):
        """Generate markdown content using selected API"""
        example = """💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시

▶ 표결 현황:
• "vote-a-rama" 새벽까지 지속, 종료 시점 불투명
• 일출 전 최종 표결 가능성 있다고 언론 보도
• 화요일부터 계속된 수정안 표결 과정

▶ 통과 조건:
• 상원 100명 중 통상 60명 찬성 필요하지만 "reconciliation" 절차로 과반수만 필요
• 공화당 근소한 상원 장악, 민주당 강력 반대

▶ 법안 내용과 비용:
1. 2017년 트럼프 세금감면 연장
2. 신규 세금감면 도입
3. 국방·국경보안 지출 증가

▶ 내부 갈등:
• 일론 머스크 "미친 법안"이라 강력 비판, 신정당 창당 위협
• 테슬라 $TSLA 보조금 철회 위협으로 응수"""

        prompt = f"""당신은 뉴스 기사를 한국어 스타일의 마크다운 문서로 변환하는 전문가입니다.
        아래의 형식과 스타일을 정확히 따라 변환해주세요.

        필수 형식:
        1. 제목 형식: 이모지 제목내용
           예시: "💰 크라켄, 암호화폐 시장 점유율 확대 위해 혁신적인 P2P 결제앱 출시"
           - 제목 시작에 내용을 잘 표현하는 이모지 **정확히 1개만** 사용
           - 이모지는 제목의 첫 번째 문자로 위치
           - 이모지와 제목 내용 사이에 공백 하나만 사용
           - 제목은 반드시 첫 줄에 위치
           - 제목 다음에는 빈 줄 하나 추가
           - 제목은 내용을 기반으로 독자의 관심을 끌 수 있게 작성
           - 단순 사실 나열보다는 핵심 가치나 의미를 담아 작성
           - **중요**: 이모지는 반드시 1개만, 여러 개 사용 금지

        2. 섹션 구조:
           - 각 주요 섹션은 ▶로 시작
           - 섹션 제목은 명사형으로 끝남 (예: "현황:", "전망:", "영향:")
           - 섹션 제목 뒤에는 반드시 콜론(:) 사용

        3. 글머리 기호:
           - 주요 사실/현황은 • 기호 사용
           - 순차적 내용이나 상세 설명은 1. 2. 3. 번호 사용
           - 인용구나 발언은 따옴표(" ") 사용

        4. 문체와 톤:
           - 객관적이고 명확한 문체 사용
           - 문장은 간결하게, 되도록 1-2줄 이내로 작성
           - 전문 용어는 가능한 한글로 풀어서 설명
           - 숫자나 통계는 단위와 함께 명확히 표기

        5. 구조화:
           - 중요도와 시간 순서를 고려한 섹션 배치
           - 관련 내용은 같은 섹션에 모아서 정리
           - 섹션 간 적절한 줄바꿈으로 가독성 확보
           - 마지막에는 향후 전망이나 결론 포함

        6. 특별 규칙:
           - 주식 종목명이 나오면 반드시 종목명 뒤에 $심볼 표기
           예: 테슬라 $TSLA, 애플 $AAPL
           - 괄호 사용하지 않고 공백으로 구분

        7. 제외할 내용:
           - 기자 소개나 프로필 정보 (예: "에마 오커먼은 야후 파이낸스에서...")
           - 기자 연락처나 이메일 정보 (예: "emma.ockerman@yahooinc.com으로 이메일을 보내세요")
           - 기자 경력이나 소속 언론사 소개
           - 기사 마지막의 기자 정보 블록 전체
           - 기자 관련 모든 개인 정보나 연락처
           - 홍보성 메시지나 광고 문구 (예: "지금 구독하세요", "더 많은 정보를 원하시면...")
           - 뉴스레터 구독 안내나 마케팅 메시지
           - 소셜 미디어 팔로우 유도 문구
           - 앱 다운로드나 서비스 가입 권유
           - 상업적 홍보나 광고성 콘텐츠

        예시 형식:
        {example}

        입력 데이터:
        제목: {content['title']}
        설명: {content['description']}
        본문: {content['content']}

        제목은 반드시 첫 줄에 위치하고, 내용을 잘 표현하는 이모지 하나를 시작에 넣어주세요.
        제목은 단순히 사실을 나열하는 것이 아니라, 내용의 핵심 가치나 의미를 담아 독자의 관심을 끌 수 있게 작성해주세요.
        
        이모지 선택 가이드:
        - 금융/투자 관련: 💰 💵 📈 📊
        - 기술/혁신 관련: 🚀 💡 🔧 🌟
        - 정책/규제 관련: ⚖️ 📜 🏛️ 🔨
        - 갈등/경쟁 관련: 🔥 ⚔️ 🎯 🎲
        - 협력/계약 관련: 🤝 📝 🎊 🌈
        - 성장/발전 관련: 🌱 🎉 💪 ⭐
        """
        
        response = self.call_api(prompt, max_tokens=2000)
        response = self.clean_response(response)
        
        # Ensure the title is properly formatted with exactly one emoji
        lines = response.split('\n')
        title_line = lines[0].strip()
        
        # Simple emoji detection and formatting
        import re
        
        # Check if title starts with an emoji (common emoji ranges)
        emoji_chars = ['💰', '💵', '📈', '📊', '🚀', '💡', '🔧', '🌟', '⚖️', '📜', '🏛️', '🔨', '🔥', '⚔️', '🎯', '🎲', '🤝', '📝', '🎊', '🌈', '🌱', '🎉', '💪', '⭐', '📰', '⚠️', '💱', '🚗', '⛽', '🤖', '💻', '📱', '🏦', '🏢', '🌍', '🇺🇸', '🇨🇳', '🇯🇵', '🇰🇷', '🇪🇺']
        
        # Count emojis in title
        emoji_count = sum(1 for emoji in emoji_chars if emoji in title_line)
        
        if emoji_count == 0:
            # No emoji found, add default emoji
            title = title_line if len(title_line) > 10 else content['title']
            formatted_title = f"📰 {title}\n"
            response = formatted_title + '\n'.join(lines[1:])
        elif emoji_count > 1:
            # Multiple emojis found, keep only the first one
            for emoji in emoji_chars:
                if emoji in title_line:
                    # Remove all emojis and add back only the first one
                    text_without_emojis = title_line
                    for e in emoji_chars:
                        text_without_emojis = text_without_emojis.replace(e, '')
                    formatted_title = f"{emoji} {text_without_emojis.strip()}\n"
                    response = formatted_title + '\n'.join(lines[1:])
                    break
        
        # Fix stock symbol format
        response = re.sub(r'(\w+)\((\$[A-Z]+)\)', r'\1 \2', response)
        
        return response

    def convert_to_markdown(self, data):
        """Convert parsed data to markdown format"""
        # Generate markdown content
        markdown_content = self.generate_markdown_content(data)
        
        # Extract keywords
        keywords = self.extract_keywords(f"{data['title']}\n{data['description']}\n{data['content']}")
        
        # Combine content and keywords with proper spacing
        final_content = f"{markdown_content}\n\n{keywords}"
        
        return final_content

    def process_file(self, file_path):
        """Process a single TXT file"""
        print(f"Processing {file_path} with {self.api_provider} API...")
        data = self.read_txt_file(file_path)
        markdown_content = self.convert_to_markdown(data)
        
        # Create output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_filename = f"{Path(file_path).stem}_{timestamp}.md"
        output_path = self.output_dir / output_filename
        
        # Save markdown content
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"Created {output_path}")

    def process_directory(self, directory_path):
        """Process all TXT files in a directory"""
        directory = Path(directory_path)
        for txt_file in directory.glob('*.txt'):
            self.process_file(txt_file)

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python converter.py <txt_file_or_directory> [api_provider]")
        print("api_provider options: anthropic (default) or openai")
        print("\nExamples:")
        print("  python converter.py article.txt")
        print("  python converter.py article.txt openai")
        print("  python converter.py ./articles/")
        print("  python converter.py ./articles/ openai")
        sys.exit(1)
    
    path = sys.argv[1]
    api_provider = sys.argv[2] if len(sys.argv) > 2 else 'anthropic'
    
    # Validate API provider
    if api_provider not in ['anthropic', 'openai']:
        print("Error: api_provider must be 'anthropic' or 'openai'")
        sys.exit(1)
    
    # Check if required API key is set
    if api_provider == 'anthropic' and not os.getenv('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY environment variable is required")
        print("Please set your Anthropic API key in the .env file")
        sys.exit(1)
    elif api_provider == 'openai' and not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY environment variable is required")
        print("Please set your OpenAI API key in the .env file")
        sys.exit(1)
    
    converter = NewsConverter(api_provider=api_provider)
    
    if os.path.isfile(path):
        converter.process_file(path)
    elif os.path.isdir(path):
        converter.process_directory(path)
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

if __name__ == '__main__':
    main() 