"""
NewsForge Pro - FastAPI Backend Service
Enterprise-grade news to markdown conversion service
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import uvicorn
from typing import Optional, Dict, Any, List
import logging
import sys
from datetime import datetime
import os
import uuid
from pydantic import BaseModel, Field

# Configure enterprise-grade logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('newsforge.log')
    ]
)

logger = logging.getLogger(__name__)

# Simplified service implementations for immediate deployment
class ConverterService:
    """News conversion service"""
    def __init__(self):
        self.tasks = {}
        
    async def initialize(self):
        logger.info("ConverterService initialized")
        
    async def cleanup(self):
        logger.info("ConverterService cleanup completed")
        
    async def convert_async(self, **kwargs):
        task_id = str(uuid.uuid4())
        
        # Extract user API key and provider
        api_key = kwargs.get('api_key')
        api_provider = kwargs.get('api_provider')
        url = kwargs.get('url')
        
        logger.info(f"Starting conversion with {api_provider} API key: {api_key[:10] if api_key else 'None'}...")
        
        # Store task info
        self.tasks[task_id] = {
            "status": "processing",
            "progress": 0,
            "current_step": "뉴스 기사 추출 중",
            "api_key": api_key,
            "api_provider": api_provider,
            "url": url
        }
        
        # Start background processing
        asyncio.create_task(self._process_conversion(task_id))
        
        return task_id
    
    async def _process_conversion(self, task_id: str):
        """실제 변환 프로세스 - 뉴스 추출 후 AI 변환"""
        try:
            task_data = self.tasks[task_id]
            
            # 1. 뉴스 추출 단계
            self.tasks[task_id].update({
                "progress": 10,
                "current_step": "뉴스 기사 추출 중"
            })
            
            # 실제 뉴스 추출 
            article_content = await self._extract_news_content(task_data['url'])
            
            if not article_content:
                raise Exception("뉴스 기사를 추출할 수 없습니다.")
                
            # 2. AI 변환 단계
            self.tasks[task_id].update({
                "progress": 50,
                "current_step": "AI 변환 중"
            })
            
            # 사용자 API 키로 AI 호출
            api_key = task_data['api_key']
            api_provider = task_data['api_provider']
            
            if api_provider == 'openai':
                content = await self._convert_with_openai(article_content, api_key)
            elif api_provider == 'anthropic':
                content = await self._convert_with_anthropic(article_content, api_key)
            else:
                raise Exception("지원되지 않는 API 제공업체입니다.")
            
            # 완료
            self.tasks[task_id].update({
                "status": "completed",
                "progress": 100,
                "current_step": "완료",
                "converted_content": content
            })
            
        except Exception as e:
            logger.error(f"Conversion failed for task {task_id}: {str(e)}")
            self.tasks[task_id].update({
                "status": "failed",
                "current_step": "오류 발생",
                "error": str(e)
            })
    
    async def _extract_news_content(self, url: str) -> dict:
        """뉴스 콘텐츠 실제 추출"""
        try:
            import httpx
            from bs4 import BeautifulSoup
            
            # HTTP 요청으로 페이지 가져오기
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                # BeautifulSoup으로 HTML 파싱
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # 제목 추출
                title = ""
                title_selectors = ['h1', '.headline', '.title', 'h1[data-module="ArticleHeader"]']
                for selector in title_selectors:
                    title_elem = soup.select_one(selector)
                    if title_elem:
                        title = title_elem.get_text().strip()
                        break
                
                if not title:
                    title_elem = soup.find('title')
                    if title_elem:
                        title = title_elem.get_text().strip()
                
                # 본문 추출 - Yahoo Finance 특화
                content = ""
                content_selectors = [
                    '.caas-body',  # Yahoo Finance main content
                    '[data-module="ArticleBody"]',
                    '.article-content',
                    '.story-body',
                    '.post-content',
                    '.entry-content',
                    'article',
                    '.content'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        # 불필요한 태그 제거
                        for tag in content_elem.find_all(['script', 'style', 'nav', 'footer', 'aside']):
                            tag.decompose()
                        
                        content = content_elem.get_text().strip()
                        if len(content) > 100:  # 충분한 내용이 있으면 사용
                            break
                
                # 내용이 부족하면 전체 body에서 추출
                if len(content) < 100:
                    body = soup.find('body')
                    if body:
                        # 불필요한 태그 제거
                        for tag in body.find_all(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                            tag.decompose()
                        content = body.get_text()
                
                # 텍스트 정리
                import re
                content = re.sub(r'\s+', ' ', content).strip()
                content = content[:5000]  # 5000자로 제한
                
                logger.info(f"뉴스 추출 완료 - 제목: {title[:50]}..., 내용: {len(content)}자")
                
                return {
                    "title": title,
                    "content": content,
                    "url": url
                }
                
        except Exception as e:
            logger.error(f"뉴스 추출 실패: {str(e)}")
            raise Exception(f"기사 추출 실패: {str(e)}")
    
    async def _convert_with_openai(self, article_data: dict, api_key: str) -> str:
        """OpenAI API를 사용한 마크다운 변환"""
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=api_key)
            
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            url = article_data.get('url', '')
            
            # 사용자 맞춤형 상세 마크다운 변환 프롬프트
            example = """🛍️ 소비자들, 프라임 데이와 대형 세일 기간 중 조기 학용품 쇼핑 급증

▶ 주요 동향:
• 전국소매연맹 보고서에 따르면 미국인들이 개학 쇼핑을 조기에 시작하는 추세
• 팬데믹 이후 시작된 트렌드가 올해 더욱 가속화
• 가계 예산 압박과 7월 대형 세일이 주요 요인

▶ 주요 세일 일정:
1. 아마존 $AMZN 프라임 데이 7월 8-11일 진행
2. 월마트 $WMT 세일 7월 8-13일 
3. 타겟 $TGT 프로모션 7월 6-12일
4. 베스트바이 $BBY 이벤트 내일 종료

▶ 시장 전망:
• 뱅크오브아메리카는 "프라임 데이가 아마존에 210억 달러 이상의 매출을 창출할 것"이라고 예측
• 6월 초까지 4분의 1 이상의 소비자가 이미 개학 쇼핑 시작
• 관세 우려로 인한 조기 구매 심리 확산"""

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
   - 섹션 제목은 뉴스 내용에 맞게 유연하게 작성 (예: "주요 동향:", "시장 반응:", "향후 전망:", "업계 분석:", "정책 변화:" 등)
   - 섹션 제목은 명사형으로 끝남
   - 섹션 제목 뒤에는 반드시 콜론(:) 사용
   - 고정된 섹션명 사용 금지, 내용에 맞는 적절한 섹션명 사용

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
   예: 테슬라 $TSLA, 애플 $AAPL, 아마존 $AMZN, 월마트 $WMT
   - 괄호 사용하지 않고 공백으로 구분

7. 제외할 내용:
   - 기자 소개나 프로필 정보
   - 기자 연락처나 이메일 정보
   - 기자 경력이나 소속 언론사 소개
   - 홍보성 메시지나 광고 문구
   - 뉴스레터 구독 안내나 마케팅 메시지
   - 상업적 홍보나 광고성 콘텐츠

예시 형식:
{example}

이모지 선택 가이드:
- 금융/투자 관련: 💰 💵 📈 📊
- 기술/혁신 관련: 🚀 💡 🔧 🌟
- 정책/규제 관련: ⚖️ 📜 🏛️ 🔨
- 갈등/경쟁 관련: 🔥 ⚔️ 🎯 🎲
- 협력/계약 관련: 🤝 📝 🎊 🌈
- 성장/발전 관련: 🌱 🎉 💪 ⭐
- 쇼핑/소비 관련: 🛍️ 🛒 💳 🏬

입력 데이터:
제목: {title}
URL: {url}
내용: {content}

제목은 반드시 첫 줄에 위치하고, 내용을 잘 표현하는 이모지 하나를 시작에 넣어주세요.
제목은 단순히 사실을 나열하는 것이 아니라, 내용의 핵심 가치나 의미를 담아 독자의 관심을 끌 수 있게 작성해주세요.
섹션명은 뉴스 내용에 맞게 유연하게 작성하되, 반드시 ▶ 기호로 시작하고 콜론(:)으로 끝내주세요.

**중요한 문장 작성 규칙**:
- 한 문장은 최대 30자 이내로 작성
- 복잡한 조건문은 반드시 여러 문장으로 분리
- 예시: "현재 연간 20만 달러 이하를 벌거나 공동으로 신고하는 경우 40만 달러 이하를 벌면, 17세 이하의 자녀를 부양 가족으로 신고하면 최대 2,000달러의 부분 환급 세액공제를 받을 수 있음" 
- 위 문장은 다음과 같이 분리: "현재 세액공제 조건은 다음과 같음" / "개인 연소득 20만 달러 이하 또는 부부합산 40만 달러 이하" / "17세 이하 자녀 부양 시 최대 2,000달러 공제"
- 한 문장에는 하나의 핵심 정보만 포함
- 접속사("~하면서", "~하는 경우")로 연결된 복잡한 문장은 반드시 분리
"""
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 뉴스 기사를 한국어 스타일의 구조화된 마크다운으로 변환하는 전문가입니다. 사용자가 지정한 형식을 정확히 따라주세요. 섹션명은 고정하지 말고 뉴스 내용에 맞게 유연하게 작성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content or "변환 완료"
            logger.info(f"OpenAI 변환 완료: {len(result)}자")
            return result
            
        except Exception as e:
            raise Exception(f"OpenAI API call failed: {str(e)}")
    
    async def _convert_with_anthropic(self, article_data: dict, api_key: str) -> str:
        """Anthropic API를 사용한 마크다운 변환"""
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            title = article_data.get('title', '')
            content = article_data.get('content', '')
            url = article_data.get('url', '')
            
            # 사용자 맞춤형 상세 마크다운 변환 프롬프트
            example = """🛍️ 소비자들, 프라임 데이와 대형 세일 기간 중 조기 학용품 쇼핑 급증

▶ 주요 동향:
• 전국소매연맹 보고서에 따르면 미국인들이 개학 쇼핑을 조기에 시작하는 추세
• 팬데믹 이후 시작된 트렌드가 올해 더욱 가속화
• 가계 예산 압박과 7월 대형 세일이 주요 요인

▶ 주요 세일 일정:
1. 아마존 $AMZN 프라임 데이 7월 8-11일 진행
2. 월마트 $WMT 세일 7월 8-13일 
3. 타겟 $TGT 프로모션 7월 6-12일
4. 베스트바이 $BBY 이벤트 내일 종료

▶ 시장 전망:
• 뱅크오브아메리카는 "프라임 데이가 아마존에 210억 달러 이상의 매출을 창출할 것"이라고 예측
• 6월 초까지 4분의 1 이상의 소비자가 이미 개학 쇼핑 시작
• 관세 우려로 인한 조기 구매 심리 확산"""

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
   - 섹션 제목은 뉴스 내용에 맞게 유연하게 작성 (예: "주요 동향:", "시장 반응:", "향후 전망:", "업계 분석:", "정책 변화:" 등)
   - 섹션 제목은 명사형으로 끝남
   - 섹션 제목 뒤에는 반드시 콜론(:) 사용
   - 고정된 섹션명 사용 금지, 내용에 맞는 적절한 섹션명 사용

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
   예: 테슬라 $TSLA, 애플 $AAPL, 아마존 $AMZN, 월마트 $WMT
   - 괄호 사용하지 않고 공백으로 구분

7. 제외할 내용:
   - 기자 소개나 프로필 정보
   - 기자 연락처나 이메일 정보
   - 기자 경력이나 소속 언론사 소개
   - 홍보성 메시지나 광고 문구
   - 뉴스레터 구독 안내나 마케팅 메시지
   - 상업적 홍보나 광고성 콘텐츠

예시 형식:
{example}

이모지 선택 가이드:
- 금융/투자 관련: 💰 💵 📈 📊
- 기술/혁신 관련: 🚀 💡 🔧 🌟
- 정책/규제 관련: ⚖️ 📜 🏛️ 🔨
- 갈등/경쟁 관련: 🔥 ⚔️ 🎯 🎲
- 협력/계약 관련: 🤝 📝 🎊 🌈
- 성장/발전 관련: 🌱 🎉 💪 ⭐
- 쇼핑/소비 관련: 🛍️ 🛒 💳 🏬

입력 데이터:
제목: {title}
URL: {url}
내용: {content}

제목은 반드시 첫 줄에 위치하고, 내용을 잘 표현하는 이모지 하나를 시작에 넣어주세요.
제목은 단순히 사실을 나열하는 것이 아니라, 내용의 핵심 가치나 의미를 담아 독자의 관심을 끌 수 있게 작성해주세요.
섹션명은 뉴스 내용에 맞게 유연하게 작성하되, 반드시 ▶ 기호로 시작하고 콜론(:)으로 끝내주세요.

**중요한 문장 작성 규칙**:
- 한 문장은 최대 30자 이내로 작성
- 복잡한 조건문은 반드시 여러 문장으로 분리
- 예시: "현재 연간 20만 달러 이하를 벌거나 공동으로 신고하는 경우 40만 달러 이하를 벌면, 17세 이하의 자녀를 부양 가족으로 신고하면 최대 2,000달러의 부분 환급 세액공제를 받을 수 있음" 
- 위 문장은 다음과 같이 분리: "현재 세액공제 조건은 다음과 같음" / "개인 연소득 20만 달러 이하 또는 부부합산 40만 달러 이하" / "17세 이하 자녀 부양 시 최대 2,000달러 공제"
- 한 문장에는 하나의 핵심 정보만 포함
- 접속사("~하면서", "~하는 경우")로 연결된 복잡한 문장은 반드시 분리
"""
            
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            logger.info(f"Anthropic 변환 완료: {len(result)}자")
            return result
            
        except Exception as e:
            raise Exception(f"Anthropic API call failed: {str(e)}")
        
    async def get_result(self, task_id: str, user_id: int):
        return self.tasks.get(task_id)

class UserService:
    """User management service"""
    def __init__(self):
        pass
        
    async def initialize(self):
        logger.info("UserService initialized")
        
    async def increment_usage(self, user_id: int):
        logger.info(f"Usage incremented for user {user_id}")
        
    async def get_usage_stats(self, user_id: int):
        return {"daily_usage": 1, "monthly_usage": 5}

class RateLimiter:
    """Rate limiting service"""
    def __init__(self):
        pass
        
    async def check_user_limit(self, user_id: int, user_plan: str):
        return {"allowed": True}

# Pydantic models
class ConversionRequest(BaseModel):
    url: str = Field(..., description="News article URL")
    platforms: List[str] = Field(default=["twitter"], description="Target platforms")
    converter_type: str = Field(default="openai", description="AI converter type")
    api_key: Optional[str] = Field(None, description="User provided API key")
    api_provider: Optional[str] = Field(None, description="API provider")

class ConversionResponse(BaseModel):
    success: bool
    task_id: Optional[str] = None
    message: str
    estimated_time: Optional[int] = None

class ConversionResult(BaseModel):
    status: str
    converted_content: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[int] = None
    current_step: Optional[str] = None

class NewsForgeException(Exception):
    pass

async def get_current_user():
    return {"id": 1, "plan": "free"}

# Global service instances
converter_service = ConverterService()
user_service = UserService()
rate_limiter = RateLimiter()

# Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle"""
    logger.info("🚀 NewsForge Pro API Starting...")
    
    # Initialize services
    try:
        await converter_service.initialize()
        await user_service.initialize()
        logger.info("✅ All services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")
    
    yield
    
    # Cleanup
    logger.info("🛑 NewsForge Pro API Shutting down...")
    try:
        await converter_service.cleanup()
        logger.info("✅ Cleanup completed")
    except Exception as e:
        logger.error(f"❌ Cleanup failed: {e}")

# FastAPI app initialization
app = FastAPI(
    title="NewsForge Pro API",
    description="Enterprise News to Markdown Conversion Service",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS configuration for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001", 
        "https://newsforge.pro",
        "https://www.newsforge.pro"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Correlation ID middleware
@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    """Add correlation ID to all requests for tracing"""
    correlation_id = str(uuid.uuid4())
    request.state.correlation_id = correlation_id
    
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    
    return response

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "NewsForge Pro API"
    }

# Main conversion endpoint
@app.post("/api/v1/convert", response_model=ConversionResponse)
async def convert_news(
    request: ConversionRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """
    Convert news article to markdown content
    
    - **url**: News article URL to convert
    - **platforms**: Target platforms (twitter, threads, linkedin, instagram)  
    - **converter_type**: AI converter type (openai, anthropic, auto)
    - **api_key**: User provided API key
    - **api_provider**: API provider (openai, anthropic)
    """
    
    try:
        logger.info(f"Conversion request: {request.url} by user {current_user['id']}")
        logger.info(f"API Provider: {request.api_provider}, API Key: {request.api_key[:10] if request.api_key else 'None'}...")
        
        # Validate API key
        if not request.api_key or not request.api_provider:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API 키와 제공업체를 설정해주세요."
            )
        
        # Rate limiting check
        usage_check = await rate_limiter.check_user_limit(
            user_id=current_user["id"],
            user_plan=current_user.get("plan", "free")
        )
        
        if not usage_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Usage limit exceeded",
                    "message": "업그레이드하여 무제한 사용하세요",
                    "upgrade_url": "/pricing",
                    "current_usage": usage_check.get("current_usage", 0),
                    "limit": usage_check.get("limit", 0)
                }
            )
        
        # Start async conversion task
        task_id = await converter_service.convert_async(
            url=request.url,
            user_id=current_user["id"],
            platforms=request.platforms,
            converter_type=request.converter_type,
            api_key=request.api_key,
            api_provider=request.api_provider
        )
        
        # Increment usage in background
        background_tasks.add_task(
            user_service.increment_usage,
            current_user["id"]
        )
        
        logger.info(f"Conversion task started: {task_id}")
        
        return ConversionResponse(
            success=True,
            task_id=task_id,
            message="변환 작업이 시작되었습니다",
            estimated_time=30
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "변환 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            }
        )

# Get conversion result
@app.get("/api/v1/conversion/{task_id}", response_model=ConversionResult)
async def get_conversion_result(
    task_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get conversion task result"""
    
    try:
        result = await converter_service.get_result(task_id, current_user["id"])
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversion task not found"
            )
        
        return ConversionResult(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Result retrieval error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="결과 조회 중 오류가 발생했습니다."
        )

# User usage statistics
@app.get("/api/v1/user/usage")
async def get_user_usage(current_user: dict = Depends(get_current_user)):
    """Get user usage statistics"""
    
    try:
        usage_info = await user_service.get_usage_stats(current_user["id"])
        return usage_info
    except Exception as e:
        logger.error(f"Usage stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="사용량 조회 중 오류가 발생했습니다."
        )

# User history
@app.get("/api/v1/user/history")
async def get_user_history(
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user conversion history"""
    
    return {
        "history": [],
        "total": 0,
        "limit": limit,
        "offset": offset
    }

# Subscription management
@app.post("/api/v1/subscribe")
async def create_subscription(
    plan: str,
    current_user: dict = Depends(get_current_user)
):
    """Create premium subscription"""
    
    # TODO: Implement Stripe payment processing
    return {
        "message": "구독 기능은 곧 출시됩니다",
        "plan": plan,
        "contact": "support@newsforge.pro"
    }

# Global exception handlers
@app.exception_handler(NewsForgeException)
async def newsforge_exception_handler(request: Request, exc: NewsForgeException):
    """Handle NewsForge specific exceptions"""
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": exc.__class__.__name__,
            "message": str(exc),
            "correlation_id": getattr(request.state, 'correlation_id', None)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "InternalServerError", 
            "message": "내부 서버 오류가 발생했습니다.",
            "correlation_id": getattr(request.state, 'correlation_id', None)
        }
    )

# Development server runner
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 