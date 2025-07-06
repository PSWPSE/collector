"""
중앙집중식 콘텐츠 생성 가이드라인 관리
모든 콘텐츠 생성 프롬프트와 가이드라인을 한 곳에서 관리
"""

from typing import Dict, List


class ContentGuidelines:
    """콘텐츠 생성 가이드라인 중앙 관리 클래스"""
    
    # 이모지 카테고리별 분류
    EMOJI_CATEGORIES = {
        'finance': ['💰', '💵', '📈', '📊'],
        'technology': ['🚀', '💡', '🔧', '🌟'],
        'policy': ['⚖️', '📜', '🏛️', '🔨'],
        'conflict': ['🔥', '⚔️', '🎯', '🎲'],
        'cooperation': ['🤝', '📝', '🎊', '🌈'],
        'growth': ['🌱', '🎉', '💪', '⭐'],
        'news': ['📰', '⚠️', '💱', '🚗', '⛽'],
        'tech_companies': ['🤖', '💻', '📱', '🏦', '🏢'],
        'global': ['🌍', '🇺🇸', '🇨🇳', '🇯🇵', '🇰🇷', '🇪🇺']
    }
    
    # 표준 예시 템플릿
    EXAMPLE_TEMPLATE = """🤝 시진핑-트럼프 회담 준비, 시간 촉박

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

    @classmethod
    def get_main_prompt_template(cls) -> str:
        """메인 프롬프트 템플릿 반환"""
        return """당신은 뉴스 기사를 한국어 스타일의 마크다운 문서로 변환하는 전문가입니다.
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
제목: {title}
설명: {description}
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

    @classmethod
    def get_formatted_prompt(cls, title: str, description: str = "", content: str = "") -> str:
        """포맷팅된 프롬프트 반환"""
        template = cls.get_main_prompt_template()
        return template.format(
            example=cls.EXAMPLE_TEMPLATE,
            title=title,
            description=description,
            content=content
        )
    
    @classmethod
    def get_emoji_for_category(cls, category: str) -> List[str]:
        """카테고리별 이모지 목록 반환"""
        return cls.EMOJI_CATEGORIES.get(category, cls.EMOJI_CATEGORIES['news'])
    
    @classmethod
    def get_all_emojis(cls) -> List[str]:
        """모든 이모지 목록 반환"""
        all_emojis = []
        for emojis in cls.EMOJI_CATEGORIES.values():
            all_emojis.extend(emojis)
        return list(set(all_emojis))  # 중복 제거
    
    @classmethod
    def validate_emoji_format(cls, text: str) -> bool:
        """이모지 포맷 검증"""
        lines = text.split('\n')
        if not lines:
            return False
        
        title_line = lines[0].strip()
        all_emojis = cls.get_all_emojis()
        
        # 제목에 이모지가 있는지 확인
        emoji_count = sum(1 for emoji in all_emojis if emoji in title_line)
        
        # 정확히 1개의 이모지가 있고, 제목 시작에 있는지 확인
        if emoji_count == 1:
            for emoji in all_emojis:
                if title_line.startswith(emoji + ' '):
                    return True
        
        return False
    
    @classmethod
    def fix_emoji_format(cls, text: str) -> str:
        """이모지 포맷 자동 수정"""
        lines = text.split('\n')
        if not lines:
            return text
        
        title_line = lines[0].strip()
        all_emojis = cls.get_all_emojis()
        
        # 이모지 개수 확인
        emoji_count = sum(1 for emoji in all_emojis if emoji in title_line)
        
        if emoji_count == 0:
            # 이모지가 없으면 기본 이모지 추가
            formatted_title = f"📰 {title_line}"
        elif emoji_count > 1:
            # 여러 이모지가 있으면 첫 번째만 유지
            first_emoji = None
            for emoji in all_emojis:
                if emoji in title_line:
                    first_emoji = emoji
                    break
            
            # 모든 이모지 제거 후 첫 번째 이모지만 추가
            clean_title = title_line
            for emoji in all_emojis:
                clean_title = clean_title.replace(emoji, '')
            
            formatted_title = f"{first_emoji} {clean_title.strip()}"
        else:
            # 정확히 1개의 이모지가 있는 경우
            formatted_title = title_line
        
        # 수정된 제목으로 교체
        lines[0] = formatted_title
        return '\n'.join(lines)
    
    @classmethod
    def format_stock_symbols(cls, text: str) -> str:
        """주식 심볼 포맷팅"""
        import re
        # (NASDAQ: TSLA) → $TSLA 형태로 변환
        text = re.sub(r'\(NASDAQ:\s*([A-Z]+)\)', r' $\1', text)
        text = re.sub(r'\(NYSE:\s*([A-Z]+)\)', r' $\1', text)
        text = re.sub(r'\(([A-Z]{1,5})\)', r' $\1', text)  # 일반적인 심볼
        
        return text


# 전역 인스턴스
content_guidelines = ContentGuidelines()


# 편의 함수들
def get_content_prompt(title: str, description: str = "", content: str = "") -> str:
    """콘텐츠 생성 프롬프트 가져오기"""
    return content_guidelines.get_formatted_prompt(title, description, content)


def validate_content_format(text: str) -> bool:
    """콘텐츠 포맷 검증"""
    return content_guidelines.validate_emoji_format(text)


def fix_content_format(text: str) -> str:
    """콘텐츠 포맷 자동 수정"""
    # 이모지 포맷 수정
    text = content_guidelines.fix_emoji_format(text)
    
    # 주식 심볼 포맷 수정
    text = content_guidelines.format_stock_symbols(text)
    
    return text


def get_emoji_suggestions(category: str = 'news') -> List[str]:
    """카테고리별 이모지 제안"""
    return content_guidelines.get_emoji_for_category(category) 