"""
OpenAI GPT API 기반 뉴스 변환기

GPT-4o 모델을 사용하여 뉴스 기사를 고품질 마크다운으로 변환합니다.
"""

import os
import re
from typing import Dict
from openai import OpenAI
from .base_converter import BaseConverter


class OpenAIConverter(BaseConverter):
    """OpenAI GPT API 기반 변환기"""
    
    def __init__(self, output_dir: str = 'data/generated'):
        """
        OpenAI 변환기 초기화
        
        Args:
            output_dir: 출력 디렉토리 경로
        """
        super().__init__(output_dir)
        
        # OpenAI 클라이언트 초기화
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(api_key=api_key)
        print("🤖 Using OpenAI GPT API")
    
    def call_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0) -> str:
        """
        OpenAI API 호출
        
        Args:
            prompt: 입력 프롬프트
            max_tokens: 최대 토큰 수
            temperature: 창의성 수준
            
        Returns:
            API 응답 텍스트
        """
        try:
            response = self.client.chat.completions.create(
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
            content = response.choices[0].message.content
            if content is None:
                raise RuntimeError("OpenAI API returned empty response")
            return content
            
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")
    
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