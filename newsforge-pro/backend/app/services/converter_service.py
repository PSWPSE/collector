"""
NewsForge Pro - 변환 서비스
검증된 추출 및 변환 로직 통합
"""

import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# 기존 검증된 모듈 임포트
import sys
sys.path.append(str(Path(__file__).parent.parent / "legacy"))

from extractors.single.web_extractor import WebExtractor
from converters.openai_converter import OpenAIConverter
from converters.anthropic_converter import AnthropicConverter

# 모의 변환기는 선택적으로 로드
try:
    from converters.mock_converter import MockConverter
    MOCK_AVAILABLE = True
except ImportError:
    MOCK_AVAILABLE = False
    MockConverter = None

logger = logging.getLogger(__name__)

class ConverterService:
    """검증된 뉴스 변환 서비스"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict] = {}
        self.temp_dir = Path("temp_conversions")
        self.temp_dir.mkdir(exist_ok=True)
        
        # 변환기 초기화
        self.converters = {
            "openai": None,
            "anthropic": None,
            "mock": MockConverter()  # 개발/테스트용 모의 변환기
        }
        
        logger.info("ConverterService 초기화 완료")
    
    async def initialize(self):
        """서비스 초기화"""
        try:
            # OpenAI 변환기 초기화
            if os.getenv('OPENAI_API_KEY'):
                self.converters["openai"] = OpenAIConverter()
                logger.info("✅ OpenAI 변환기 초기화 완료")
            
            # Anthropic 변환기 초기화  
            if os.getenv('ANTHROPIC_API_KEY'):
                self.converters["anthropic"] = AnthropicConverter()
                logger.info("✅ Anthropic 변환기 초기화 완료")
                
            if not any(self.converters.values()):
                logger.warning("⚠️ 사용 가능한 AI API 키가 없습니다")
                
        except Exception as e:
            logger.error(f"초기화 실패: {str(e)}")
    
    async def cleanup(self):
        """리소스 정리"""
        # 임시 파일 정리
        for temp_file in self.temp_dir.glob("*"):
            try:
                temp_file.unlink()
            except Exception:
                pass
        
        logger.info("ConverterService 정리 완료")
    
    async def get_converter_status(self) -> Dict[str, Any]:
        """변환기 상태 반환"""
        status = {}
        
        for name, converter in self.converters.items():
            if converter and hasattr(converter, 'is_available'):
                status[name] = {
                    "available": converter.is_available(),
                    "api_key_set": bool(os.getenv(f"{name.upper()}_API_KEY"))
                }
            else:
                status[name] = {
                    "available": False,
                    "api_key_set": bool(os.getenv(f"{name.upper()}_API_KEY"))
                }
        
        return status
    
    async def convert_async(
        self, 
        url: str, 
        user_id: int,
        platforms: Optional[List[str]] = None,
        converter_type: Optional[str] = None,
        api_key: Optional[str] = None,
        api_provider: Optional[str] = None
    ) -> str:
        """비동기 변환 작업 시작"""
        
        task_id = str(uuid.uuid4())
        
        # 기본값 설정
        if platforms is None:
            platforms = ["twitter", "threads"]
        if converter_type is None:
            converter_type = "auto"
        
        # 태스크 데이터 초기화
        self.tasks[task_id] = {
            "status": "pending",
            "progress": 0,
            "current_step": "작업 준비 중",
            "url": url,
            "user_id": user_id,
            "platforms": platforms,
            "converter_type": converter_type,
            "api_key": api_key,  # 사용자 API 키 저장
            "api_provider": api_provider,  # 사용자 API 제공업체 저장
            "created_at": datetime.utcnow().isoformat(),
            "error": None
        }
        
        # 백그라운드에서 실제 변환 작업 실행
        asyncio.create_task(self._process_conversion(task_id))
        
        return task_id
    
    async def _process_conversion(self, task_id: str):
        """실제 변환 프로세스"""
        try:
            await self._update_task_status(
                task_id, 
                status="processing",
                progress=10,
                current_step="뉴스 기사 추출 중"
            )
            
            task_data = self.tasks[task_id]
            url = task_data["url"]
            platforms = task_data["platforms"]
            converter_type = task_data["converter_type"]
            api_key = task_data.get("api_key")
            api_provider = task_data.get("api_provider")
            
            # 1. 뉴스 추출
            article_data = await self._extract_news(url)
            
            await self._update_task_status(
                task_id,
                progress=50,
                current_step="AI 변환 중",
                original_title=article_data.get("title", "")
            )
            
            # 2. AI 변환 (사용자 API 키 전달)
            converted_content = await self._convert_to_social(
                article_data, platforms, converter_type, api_key, api_provider
            )
            
            await self._update_task_status(
                task_id,
                progress=90,
                current_step="결과 정리 중"
            )
            
            # 3. 결과 저장
            final_result = {
                "status": "completed",
                "progress": 100,
                "current_step": "완료",
                "converted_content": converted_content,
                "original_title": article_data.get("title", ""),
                "original_content": self._summarize_content(article_data),
                "completed_at": datetime.utcnow().isoformat(),
                "processing_time": time.time() - datetime.fromisoformat(
                    task_data["created_at"].replace('Z', '+00:00')
                ).timestamp()
            }
            
            await self._update_task_status(task_id, **final_result)
            
        except Exception as e:
            logger.error(f"변환 실패 ({task_id}): {str(e)}")
            await self._update_task_status(
                task_id,
                status="failed",
                current_step="오류 발생",
                error=str(e)
            )
    
    async def _extract_news(self, url: str) -> Dict[str, Any]:
        """뉴스 기사 추출 (검증된 로직)"""
        logger.info(f"📰 뉴스 추출 시작: {url}")
        
        # 동적 사이트 감지
        use_selenium = any(domain in url.lower() for domain in 
                          ['yahoo', 'finance', 'bloomberg', 'cnbc', 'marketwatch'])
        
        def extract_sync():
            extractor = WebExtractor(use_selenium=use_selenium, save_to_file=False)
            try:
                data = extractor.extract_data(url)
                return data
            finally:
                extractor.close()
        
        # 별도 스레드에서 동기 추출 실행
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, extract_sync)
        
        if not result or not result.get('success'):
            raise Exception(f"기사 추출 실패: {result.get('error', '알 수 없는 오류')}")
        
        logger.info(f"✅ 추출 완료: {result.get('title', '')}")
        return result
    
    async def _convert_to_social(
        self, 
        article_data: Dict[str, Any], 
        platforms: List[str],
        converter_type: str,
        api_key: Optional[str] = None,
        api_provider: Optional[str] = None
    ) -> Dict[str, str]:
        """소셜 콘텐츠 변환"""
        
        # 변환기 선택 (사용자 API 키 우선 사용)
        converter = self._create_converter_with_user_key(converter_type, api_key, api_provider)
        if not converter:
            raise Exception("사용 가능한 AI 변환기가 없습니다")
        
        # 임시 파일 생성 (기존 변환기가 파일 기반이므로)
        temp_file = await self._create_temp_file(article_data)
        
        try:
            def convert_sync():
                # 기존 변환기 사용
                data = converter.read_txt_file(str(temp_file))
                markdown_content = converter.convert_to_markdown(data)
                keywords = converter.extract_keywords(data['content'])
                
                return {
                    "markdown": markdown_content,
                    "keywords": keywords,
                    "platforms": {
                        "twitter": self._format_for_twitter(markdown_content, keywords),
                        "threads": self._format_for_threads(markdown_content, keywords),
                        "linkedin": self._format_for_linkedin(markdown_content, keywords),
                        "instagram": self._format_for_instagram(markdown_content, keywords)
                    }
                }
            
            # 별도 스레드에서 변환 실행
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, convert_sync)
            
            # 요청된 플랫폼만 반환
            filtered_result = {
                "markdown": result["markdown"],
                "keywords": result["keywords"],
                "platforms": {k: v for k, v in result["platforms"].items() if k in platforms}
            }
            
            return filtered_result
            
        finally:
            # 임시 파일 정리
            if temp_file.exists():
                temp_file.unlink()
    
    def _create_converter_with_user_key(self, converter_type: str, api_key: Optional[str], api_provider: Optional[str]):
        """사용자 API 키로 변환기 생성 - 직접 전달 방식"""
        
        # 사용자가 API 키를 제공한 경우 우선 사용
        if api_key and api_provider:
            try:
                if api_provider == "openai":
                    # 사용자 API 키를 변환기에 직접 전달
                    from app.legacy.converters.openai_converter import OpenAIConverter
                    # 임시 환경변수 설정 없이 직접 초기화
                    converter = self._create_openai_converter_with_key(api_key)
                    logger.info(f"✅ 사용자 OpenAI API 키로 변환기 생성 완료")
                    return converter
                            
                elif api_provider == "anthropic":
                    # 사용자 API 키를 변환기에 직접 전달
                    from app.legacy.converters.anthropic_converter import AnthropicConverter
                    converter = self._create_anthropic_converter_with_key(api_key)
                    logger.info(f"✅ 사용자 Anthropic API 키로 변환기 생성 완료")
                    return converter
                            
            except Exception as e:
                logger.error(f"사용자 API 키로 변환기 생성 실패: {str(e)}")
                # 실패 시 기본 변환기 사용으로 폴백
        
        # 기본 변환기 선택 로직
        return self._select_converter(converter_type)
    
    def _create_openai_converter_with_key(self, api_key: str):
        """OpenAI 변환기를 사용자 API 키로 생성"""
        import sys
        from pathlib import Path
        
        # Legacy 모듈 임포트
        sys.path.append(str(Path(__file__).parent.parent / "legacy"))
        
        # API 키를 직접 전달하여 변환기 생성
        class UserOpenAIConverter:
            def __init__(self, api_key: str):
                import os
                from openai import OpenAI
                from app.legacy.converters.base_converter import BaseConverter
                
                self.client = OpenAI(api_key=api_key)
                self.output_dir = Path("temp_conversions")
                self.output_dir.mkdir(exist_ok=True)
                
            def call_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0) -> str:
                """OpenAI API 호출"""
                try:
                    response = self.client.chat.completions.create(
                        model="gpt-4o",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    content = response.choices[0].message.content
                    if content is None:
                        raise RuntimeError("OpenAI API returned empty response")
                    return content
                except Exception as e:
                    raise RuntimeError(f"OpenAI API call failed: {str(e)}")
            
            def read_txt_file(self, file_path: str):
                """TXT 파일 읽기"""
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 기존 파싱 로직 유지
                import re
                url_match = re.search(r'URL: (.*?)\n', content)
                title_match = re.search(r'제목: (.*?)\n', content)
                author_match = re.search(r'작성자: (.*?)\n', content)
                publish_match = re.search(r'게시일: (.*?)\n', content)
                
                # 본문 추출 (분리선 이후)
                content_match = re.search(r'={2,}\n\n(.*?)$', content, re.DOTALL)
                
                return {
                    'url': url_match.group(1) if url_match else '',
                    'title': title_match.group(1) if title_match else '',
                    'author': author_match.group(1) if author_match else '',
                    'publish_date': publish_match.group(1) if publish_match else '',
                    'description': '',  # 임시
                    'content': content_match.group(1) if content_match else content
                }
            
            def clean_content(self, content):
                """콘텐츠 정제"""
                import re
                if isinstance(content, dict) and 'paragraphs' in content:
                    text = '\n'.join(content['paragraphs'])
                elif isinstance(content, dict) and 'text' in content:
                    text = content['text']
                elif isinstance(content, str):
                    text = content
                else:
                    text = str(content)
                
                # 기자 정보 제거
                text = re.sub(r'기자[:\s].*', '', text)
                text = re.sub(r'.*@.*\.com.*', '', text)
                text = re.sub(r'구독하세요.*', '', text, flags=re.IGNORECASE)
                
                return text.strip()
            
            def format_stock_symbols(self, text):
                """주식 심볼 포맷팅"""
                import re
                
                # 주요 주식 심볼 매핑
                stock_mapping = {
                    '테슬라': 'TSLA', '애플': 'AAPL', '마이크로소프트': 'MSFT',
                    '구글': 'GOOGL', '아마존': 'AMZN', '메타': 'META',
                    '넷플릭스': 'NFLX', '엔비디아': 'NVDA'
                }
                
                for korean_name, symbol in stock_mapping.items():
                    pattern = rf'{korean_name}(?!\s*\$)'
                    replacement = f'{korean_name} ${symbol}'
                    text = re.sub(pattern, replacement, text)
                
                return text
            
            def extract_keywords(self, content: str) -> str:
                """AI 기반 키워드 추출"""
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
            
            def convert_to_markdown(self, data):
                """AI 기반 마크다운 변환 - 상세한 한국어 가이드 적용"""
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
설명: {data.get('description', '')}
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
                """이모지 형식 검증 및 수정"""
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
        
        return UserOpenAIConverter(api_key)
    
    def _create_anthropic_converter_with_key(self, api_key: str):
        """Anthropic 변환기를 사용자 API 키로 생성"""
        import sys
        from pathlib import Path
        
        # Legacy 모듈 임포트
        sys.path.append(str(Path(__file__).parent.parent / "legacy"))
        
        # API 키를 직접 전달하여 변환기 생성
        class UserAnthropicConverter:
            def __init__(self, api_key: str):
                import anthropic
                from app.legacy.converters.base_converter import BaseConverter
                
                self.client = anthropic.Anthropic(api_key=api_key)
                self.output_dir = Path("temp_conversions")
                self.output_dir.mkdir(exist_ok=True)
                
            def call_api(self, prompt: str, max_tokens: int = 2000, temperature: float = 0) -> str:
                """Anthropic API 호출"""
                try:
                    message = self.client.messages.create(
                        model="claude-3-opus-20240229",
                        max_tokens=max_tokens,
                        temperature=temperature,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    return self.clean_response(message.content[0])
                except Exception as e:
                    raise RuntimeError(f"Anthropic API call failed: {str(e)}")
            
            def clean_response(self, response) -> str:
                """API 응답 정제"""
                import re
                text = str(response)
                text = re.sub(r'\[.*?\]', '', text)
                text = text.replace('TextBlock(citations=None, text=', '')
                text = text.replace(', type=\'text\')', '')
                text = text.strip('"\'')
                text = text.lstrip('\n')
                text = text.replace('\\n', '\n')
                return text.strip()
                
            # 나머지 메소드들은 OpenAI와 동일하게 구현
            def read_txt_file(self, file_path: str):
                """TXT 파일 읽기"""
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 기존 파싱 로직 유지
                import re
                url_match = re.search(r'URL: (.*?)\n', content)
                title_match = re.search(r'제목: (.*?)\n', content)
                author_match = re.search(r'작성자: (.*?)\n', content)
                publish_match = re.search(r'게시일: (.*?)\n', content)
                
                # 본문 추출 (분리선 이후)
                content_match = re.search(r'={2,}\n\n(.*?)$', content, re.DOTALL)
                
                return {
                    'url': url_match.group(1) if url_match else '',
                    'title': title_match.group(1) if title_match else '',
                    'author': author_match.group(1) if author_match else '',
                    'publish_date': publish_match.group(1) if publish_match else '',
                    'description': '',  # 임시
                    'content': content_match.group(1) if content_match else content
                }
            
            def clean_content(self, content):
                """콘텐츠 정제"""
                import re
                if isinstance(content, dict) and 'paragraphs' in content:
                    text = '\n'.join(content['paragraphs'])
                elif isinstance(content, dict) and 'text' in content:
                    text = content['text']
                elif isinstance(content, str):
                    text = content
                else:
                    text = str(content)
                
                # 기자 정보 제거
                text = re.sub(r'기자[:\s].*', '', text)
                text = re.sub(r'.*@.*\.com.*', '', text)
                text = re.sub(r'구독하세요.*', '', text, flags=re.IGNORECASE)
                
                return text.strip()
            
            def format_stock_symbols(self, text):
                """주식 심볼 포맷팅"""
                import re
                
                # 주요 주식 심볼 매핑
                stock_mapping = {
                    '테슬라': 'TSLA', '애플': 'AAPL', '마이크로소프트': 'MSFT',
                    '구글': 'GOOGL', '아마존': 'AMZN', '메타': 'META',
                    '넷플릭스': 'NFLX', '엔비디아': 'NVDA'
                }
                
                for korean_name, symbol in stock_mapping.items():
                    pattern = rf'{korean_name}(?!\s*\$)'
                    replacement = f'{korean_name} ${symbol}'
                    text = re.sub(pattern, replacement, text)
                
                return text
            
            def extract_keywords(self, content: str) -> str:
                """AI 기반 키워드 추출"""
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
            
            def convert_to_markdown(self, data):
                """AI 기반 마크다운 변환 - 상세한 한국어 가이드 적용"""
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
설명: {data.get('description', '')}
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
                """이모지 형식 검증 및 수정"""
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
        
        return UserAnthropicConverter(api_key)
    
    def _select_converter(self, converter_type: str):
        """변환기 선택 (기본 로직)"""
        if converter_type == "auto":
            # 우선순위: OpenAI > Anthropic > Mock
            for name in ["openai", "anthropic", "mock"]:
                if self.converters[name] and hasattr(self.converters[name], 'is_available'):
                    if self.converters[name].is_available():
                        return self.converters[name]
                elif self.converters[name]:
                    return self.converters[name]
            return None
        
        return self.converters.get(converter_type)
    
    async def _create_temp_file(self, article_data: Dict[str, Any]) -> Path:
        """임시 TXT 파일 생성"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_file = self.temp_dir / f"article_{timestamp}_{uuid.uuid4().hex[:8]}.txt"
        
        # 기존 형식으로 파일 작성
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(f"URL: {article_data['url']}\n")
            f.write(f"제목: {article_data['title']}\n")
            f.write(f"작성자: {article_data.get('author', '')}\n")
            f.write(f"게시일: {article_data.get('publish_date', '')}\n")
            f.write(f"추출일: {article_data.get('timestamp', '')}\n")
            f.write("\n" + "="*50 + "\n\n")
            
            # 본문 내용
            content = article_data.get('content', {})
            if isinstance(content, dict) and 'paragraphs' in content:
                for paragraph in content['paragraphs']:
                    if isinstance(paragraph, str) and paragraph.strip():
                        f.write(paragraph.strip() + "\n\n")
            elif isinstance(content, dict) and 'text' in content:
                f.write(content['text'])
            elif isinstance(content, str):
                f.write(content)
        
        return temp_file
    
    def _format_for_twitter(self, markdown: str, keywords: str) -> str:
        """트위터용 포맷팅"""
        # 280자 제한 고려
        title_line = markdown.split('\n')[0] if markdown else ""
        
        # 제목에서 이모지 제거하고 간단히
        title = title_line.replace('#', '').replace('💰', '').strip()
        
        if len(title) > 200:
            title = title[:197] + "..."
        
        return f"{title}\n\n{keywords}"
    
    def _format_for_threads(self, markdown: str, keywords: str) -> str:
        """Threads용 포맷팅"""
        # 500자 제한
        lines = markdown.split('\n')
        content_lines = [line for line in lines if line.strip()][:3]
        
        content = '\n'.join(content_lines)
        if len(content) > 400:
            content = content[:397] + "..."
        
        return f"{content}\n\n{keywords}"
    
    def _format_for_linkedin(self, markdown: str, keywords: str) -> str:
        """LinkedIn용 포맷팅"""
        # 전문적인 톤으로 전체 내용 포함
        return f"{markdown}\n\n{keywords}"
    
    def _format_for_instagram(self, markdown: str, keywords: str) -> str:
        """Instagram용 포맷팅"""
        # 시각적 요소 강조
        lines = markdown.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                if line.startswith('#'):
                    formatted_lines.append(f"✨ {line.replace('#', '').strip()}")
                elif line.startswith('▶'):
                    formatted_lines.append(f"📍 {line.replace('▶', '').strip()}")
                else:
                    formatted_lines.append(line)
        
        content = '\n'.join(formatted_lines[:5])  # 처음 5줄만
        return f"{content}\n\n{keywords}"
    
    def _summarize_content(self, article_data: Dict[str, Any]) -> str:
        """내용 요약"""
        content = article_data.get('content', {})
        if isinstance(content, dict) and 'text' in content:
            text = content['text']
        elif isinstance(content, str):
            text = content
        else:
            text = str(content)
        
        # 처음 200자만 반환
        return text[:200] + "..." if len(text) > 200 else text
    
    async def _update_task_status(self, task_id: str, **kwargs):
        """태스크 상태 업데이트"""
        if task_id in self.tasks:
            self.tasks[task_id].update(kwargs)
            logger.info(f"Task {task_id}: {kwargs.get('current_step', 'status updated')}")
    
    async def get_result(self, task_id: str, user_id: int) -> Dict[str, Any]:
        """변환 결과 조회"""
        
        if task_id not in self.tasks:
            raise ValueError("Task not found")
        
        task = self.tasks[task_id]
        
        # 권한 확인
        if task.get("user_id") != user_id:
            raise PermissionError("Access denied")
        
        return task 