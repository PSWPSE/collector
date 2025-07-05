"""
Anthropic Claude API 기반 뉴스 변환기

Claude-3-Opus 모델을 사용하여 뉴스 기사를 고품질 마크다운으로 변환합니다.
"""

import os
import re
from typing import Dict
import anthropic
from .base_converter import BaseConverter


class AnthropicConverter(BaseConverter):
    """Anthropic Claude API 기반 변환기"""
    
    def __init__(self, output_dir: str = 'data/generated'):
        """
        Anthropic 변환기 초기화
        
        Args:
            output_dir: 출력 디렉토리 경로
        """
        super().__init__(output_dir)
        
        # Anthropic 클라이언트 초기화
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        print("🧠 Using Anthropic Claude API")
    
    def call_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0) -> str:
        """
        Anthropic API 호출
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 창의성 수준
            
        Returns:
            API 응답 텍스트
        """
        try:
            message = self.client.messages.create(
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
            return self.clean_response(message.content[0])
            
        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {str(e)}")
    
    def clean_response(self, response) -> str:
        """
        API 응답 정제
        
        Args:
            response: API 응답 객체
            
        Returns:
            정제된 텍스트
        """
        text = str(response)
        text = re.sub(r'\[.*?\]', '', text)
        text = text.replace('TextBlock(citations=None, text=', '')
        text = text.replace(', type=\'text\')', '')
        text = text.strip('"\'')
        text = text.lstrip('\n')
        text = text.replace('\\n', '\n')
        return text.strip()
    
    def extract_keywords(self, content: str) -> str:
        """
        AI 기반 키워드 추출
        
        Args:
            content: 분석할 내용
            
        Returns:
            해시태그 형식의 키워드
        """
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
        return response
    
    def convert_to_markdown(self, data: Dict[str, str]) -> str:
        """
        AI 기반 마크다운 변환
        
        Args:
            data: 구조화된 뉴스 데이터
            
        Returns:
            마크다운 형식의 문자열
        """
        # 내용 정제
        content = self.clean_content(data['content'])
        
        example = """🤝 시진핑-트럼프 회담 준비, 시간 촉박

▶ 회담 준비 현황:
• 미국과 중국, 가을 정상회담 준비 속도 필요
• 베이징 외교부 자문위원, "시간이 촉박하다" 강조
• 최근 양국 간 무역 휴전 합의로 긍정적 신호

▶ 양국 간 진행 상황:
1. 중국 희토류 자석 수출 재개, 이전 수준에는 미치지 못함
2. 미국, 중국에 대한 칩 설계 소프트웨어 수출 허가 요건 완화
3. 미국, 중국으로의 에탄 수출 승인

▶ 향후 계획:
• 트럼프, 중국 방문 시 기업인 동행 여부 검토 중
• 아시아태평양경제협력체(APEC) 정상회의 계기 중국 방문 가능성
• 외교 및 법 집행 기관 포함한 광범위한 논의 채널 필요

▶ 전문가 의견:
• 우신보, "트럼프는 중국을 미국의 중요한 상업 파트너로 명확히 해야"
• "대만 독립 반대 및 중국의 평화적 통일 지지 재확인 필요"
• "트럼프는 미국의 국익을 위해 적절한 발언을 할 것"

#시진핑 #트럼프 #미중정상회담 #무역협상 #중국희토류 #대만 #남중국해"""

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
   - 문장은 독자가 내용을 읽는데 간결하지만 전달하고자 하는 메세지가 무엇인지 정확하게 이해할 수 있게 짧지만 논리적이게 작성
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
제목: {data['title']}
설명: {data['description']}
본문: {content}

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
        
        # 주식 심볼 포맷팅
        response = self.format_stock_symbols(response)
        
        # 이모지 검증 및 수정
        response = self._fix_emoji_format(response)
        
        return response
    
    def _fix_emoji_format(self, text: str) -> str:
        """
        이모지 형식 검증 및 수정
        
        Args:
            text: 원본 텍스트
            
        Returns:
            이모지가 수정된 텍스트
        """
        lines = text.split('\n')
        if not lines:
            return text
            
        title_line = lines[0].strip()
        
        # 이모지 문자들
        emoji_chars = ['💰', '💵', '📈', '📊', '🚀', '💡', '🔧', '🌟', '⚖️', '📜', 
                      '🏛️', '🔨', '🔥', '⚔️', '🎯', '🎲', '🤝', '📝', '🎊', '🌈', 
                      '🌱', '🎉', '💪', '⭐', '📰', '⚠️', '💱', '🚗', '⛽', '🤖', 
                      '💻', '📱', '🏦', '🏢', '🌍', '🇺🇸', '🇨🇳', '🇯🇵', '🇰🇷', '🇪🇺']
        
        # 이모지 개수 확인
        emoji_count = sum(1 for emoji in emoji_chars if emoji in title_line)
        
        if emoji_count == 0:
            # 이모지가 없으면 기본 이모지 추가
            formatted_title = f"📰 {title_line}"
            lines[0] = formatted_title
        elif emoji_count > 1:
            # 이모지가 여러 개면 첫 번째만 유지
            for emoji in emoji_chars:
                if emoji in title_line:
                    # 모든 이모지 제거 후 첫 번째 이모지만 앞에 추가
                    text_without_emojis = title_line
                    for e in emoji_chars:
                        text_without_emojis = text_without_emojis.replace(e, '')
                    formatted_title = f"{emoji} {text_without_emojis.strip()}"
                    lines[0] = formatted_title
                    break
        
        return '\n'.join(lines) 