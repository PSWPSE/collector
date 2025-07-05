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
            
            # 참조 콘텐츠 스타일을 정확히 반영한 프롬프트
            example = """⚖️ 머스크, 트럼프 감세안에 강력 반발 "미친 법안, 공화당 정치적 자살행위"

▶ 머스크의 반대 이유:
• 부자 감세, 저소득층 복지 축소, 녹색에너지 투자 감축, 화석연료 보조금 지급
• 국가부채 최소 4조 달러 증가 초래
• "수백만 개 일자리 파괴하고 국가에 막대한 전략적 피해" 우려

▶ 법안 내용:
1. 2017년 트럼프 감세안 연장
2. 신규 감세안 도입
3. 국방·국경보안 지출 증액

▶ 상원 통과 전망:
• 민주당 강력 반대에도 불구, 공화당 근소한 다수로 통과 가능성
• "조정" 절차로 과반수만 확보하면 통과

▶ 녹색에너지 타격:
• 2022년 민주당 주도로 통과된 수천억 달러 규모 재생에너지 세액공제 폐지
• 석탄, 석유, 천연가스 산업에 유리한 조항 포함
• 전기노조 "수십만 개 건설 일자리 잃을 것" 경고

▶ 머스크의 대응:
• "공화당의 정치적 자살행위" 경고
• 새로운 정당 창당 위협
• 테슬라 $TSLA 에 대한 보조금 철회 위협에 맞대응

▶ 전망과 영향:
• 국가부채 급증과 신용등급 하락 우려
• 저소득층 실질소득 감소, 상위 20% 소득 증가
• 2026년 중간선거에서 공화당 타격 예상
• 미국 녹색에너지 경쟁력 약화, 중국에 유리

#트럼프감세안 #일론머스크 #녹색에너지 #재생에너지 #공화당 #상원법안 #세금공제"""

            prompt = f"""당신은 뉴스 기사를 한국어 스타일의 마크다운 문서로 변환하는 전문가입니다.
아래의 형식과 스타일을 정확히 따라 변환해주세요.

필수 형식 및 스타일:

1. 제목 형식: 이모지 핵심메시지 "중요한 인용구나 키워드"
   - 제목 시작에 내용을 잘 표현하는 이모지 **정확히 1개만** 사용
   - 명확하고 임팩트 있는 표현 사용 (예: "강력 반발", "급증", "발표", "확대")
   - 핵심 인물이나 기업의 직접 발언이 있으면 따옴표로 강조
   - 사실 기반의 명확한 정보 전달에 중점
   - 독자의 관심을 끌 수 있는 구체적이고 정확한 제목
   - 예시: "⚖️ 머스크, 트럼프 감세안에 강력 반발 "미친 법안, 공화당 정치적 자살행위""

2. 섹션 구조 (상황별 맞춤형):
   - 각 주요 섹션은 ▶로 시작
   - 뉴스 내용과 상황에 맞는 구체적 섹션명 사용
   - 갈등/논란: "A의 반대 이유:", "B의 대응:", "업계 반응:", "정치권 입장:"
   - 정책/법안: "법안 내용:", "통과 전망:", "찬반 의견:", "예상 영향:"
   - 기업/경제: "실적 분석:", "시장 반응:", "경쟁사 대응:", "투자자 전망:"
   - 기술/혁신: "기술 특징:", "경쟁 현황:", "도입 계획:", "업계 전망:"
   - 사건/사고: "사건 경위:", "피해 현황:", "당국 대응:", "후속 조치:"
   - 고정된 섹션명 절대 사용 금지, 반드시 뉴스 내용에 맞게 창의적으로 작성

3. 표현 스타일:
   - 객관적이고 중립적인 어조 유지
   - 사실에 기반한 명확하고 정확한 표현 사용
   - 직접 인용구를 적극 활용하여 신뢰성과 생동감 부여
   - 예: • "수백만 개 일자리 파괴하고 국가에 막대한 전략적 피해" 우려
   - 과장이나 추측보다는 확인된 사실과 공식 발언 중심

4. 글머리 기호:
   - 주요 사실/현황은 • 기호 사용
   - 순차적 내용이나 상세 설명은 1. 2. 3. 번호 사용
   - 중요한 발언이나 공식 성명은 따옴표(" ")로 강조

5. 주식 심볼 규칙:
   - 기업명 뒤에 $ 심볼과 종목 코드 표기
   - $ 심볼 앞뒤에는 반드시 공백 1칸 확보
   - 예: 테슬라 $TSLA, 애플 $AAPL, 마이크로소프트 $MSFT

6. 해시태그 추가 (필수):
   - 마지막에 뉴스와 관련된 해시태그 5-8개 추가
   - 주요 키워드, 인물명, 기업명, 정책명 등을 해시태그로 변환
   - 예: #트럼프감세안 #일론머스크 #녹색에너지 #재생에너지 #공화당 #상원법안 #세금공제

7. 이모지 선택 가이드:
   - 갈등/논란: ⚖️ ⚔️ 🔥 💥 🎯
   - 정책/정치: 🏛️ 📜 🗳️ ⚖️ 🔨
   - 경제/금융: 💰 💵 📈 📊 💸
   - 기술/혁신: 🚀 💡 🔧 🌟 ⚡
   - 기업/비즈니스: 🏢 📊 💼 🎯 🔥
   - 에너지/환경: 🌱 ⚡ 🔋 🌍 ♻️
   - 변화/발표: 💥 🚨 ⚡ 🌪️ 🎢

8. 문체와 톤:
   - 객관적이고 균형잡힌 시각으로 사실 전달
   - 갈등이나 논란은 양측 입장을 공정하게 제시
   - 숫자나 통계는 정확하고 구체적으로 표현 ("최소 4조 달러", "수십만 개")
   - 전문 용어는 한글로 풀어쓰되 정확성 유지

9. 제외할 내용:
   - 기자 정보, 연락처, 프로필
   - 광고성 메시지, 뉴스레터 구독 안내
   - 추측성이나 확인되지 않은 정보

예시 형식:
{example}

입력 데이터:
제목: {title}
URL: {url}
내용: {content}

중요한 지침:
- 제목은 명확하고 정확하게 핵심 내용 전달
- 섹션명은 뉴스 상황에 정확히 맞게 창의적으로 작성
- 직접 인용구를 적극 활용하여 신뢰성 확보
- 마지막에 관련 해시태그 반드시 포함
- 객관적이고 균형잡힌 관점으로 정보 전달
- $ 심볼 앞뒤 공백 1칸 반드시 확보

**핵심 문장 작성 원칙**:
- 사실에 기반한 정확하고 명확한 정보 전달
- 독자가 핵심 내용을 빠르게 이해할 수 있는 구조
- 공식 발언과 확인된 데이터 중심의 객관적 서술
- 인용구를 통한 신뢰성 있는 정보 제공
- 예상되는 파급효과와 영향을 사실적으로 제시
"""
            
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "당신은 뉴스 기사를 객관적이고 균형잡힌 한국어 스타일의 구조화된 마크다운으로 변환하는 전문가입니다. 사용자가 지정한 형식을 정확히 따라주세요. 사실에 기반한 정확한 정보 전달에 중점을 두고, 섹션명은 뉴스 상황에 맞게 창의적으로 작성해주세요."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.2
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
            
            # 참조 콘텐츠 스타일을 정확히 반영한 프롬프트
            example = """⚖️ 머스크, 트럼프 감세안에 강력 반발 "미친 법안, 공화당 정치적 자살행위"

▶ 머스크의 반대 이유:
• 부자 감세, 저소득층 복지 축소, 녹색에너지 투자 감축, 화석연료 보조금 지급
• 국가부채 최소 4조 달러 증가 초래
• "수백만 개 일자리 파괴하고 국가에 막대한 전략적 피해" 우려

▶ 법안 내용:
1. 2017년 트럼프 감세안 연장
2. 신규 감세안 도입
3. 국방·국경보안 지출 증액

▶ 상원 통과 전망:
• 민주당 강력 반대에도 불구, 공화당 근소한 다수로 통과 가능성
• "조정" 절차로 과반수만 확보하면 통과

▶ 녹색에너지 타격:
• 2022년 민주당 주도로 통과된 수천억 달러 규모 재생에너지 세액공제 폐지
• 석탄, 석유, 천연가스 산업에 유리한 조항 포함
• 전기노조 "수십만 개 건설 일자리 잃을 것" 경고

▶ 머스크의 대응:
• "공화당의 정치적 자살행위" 경고
• 새로운 정당 창당 위협
• 테슬라 $TSLA 에 대한 보조금 철회 위협에 맞대응

▶ 전망과 영향:
• 국가부채 급증과 신용등급 하락 우려
• 저소득층 실질소득 감소, 상위 20% 소득 증가
• 2026년 중간선거에서 공화당 타격 예상
• 미국 녹색에너지 경쟁력 약화, 중국에 유리

#트럼프감세안 #일론머스크 #녹색에너지 #재생에너지 #공화당 #상원법안 #세금공제"""

            prompt = f"""당신은 뉴스 기사를 한국어 스타일의 마크다운 문서로 변환하는 전문가입니다.
아래의 형식과 스타일을 정확히 따라 변환해주세요.

필수 형식 및 스타일:

1. 제목 형식: 이모지 핵심메시지 "중요한 인용구나 키워드"
   - 제목 시작에 내용을 잘 표현하는 이모지 **정확히 1개만** 사용
   - 명확하고 임팩트 있는 표현 사용 (예: "강력 반발", "급증", "발표", "확대")
   - 핵심 인물이나 기업의 직접 발언이 있으면 따옴표로 강조
   - 사실 기반의 명확한 정보 전달에 중점
   - 독자의 관심을 끌 수 있는 구체적이고 정확한 제목
   - 예시: "⚖️ 머스크, 트럼프 감세안에 강력 반발 "미친 법안, 공화당 정치적 자살행위""

2. 섹션 구조 (상황별 맞춤형):
   - 각 주요 섹션은 ▶로 시작
   - 뉴스 내용과 상황에 맞는 구체적 섹션명 사용
   - 갈등/논란: "A의 반대 이유:", "B의 대응:", "업계 반응:", "정치권 입장:"
   - 정책/법안: "법안 내용:", "통과 전망:", "찬반 의견:", "예상 영향:"
   - 기업/경제: "실적 분석:", "시장 반응:", "경쟁사 대응:", "투자자 전망:"
   - 기술/혁신: "기술 특징:", "경쟁 현황:", "도입 계획:", "업계 전망:"
   - 사건/사고: "사건 경위:", "피해 현황:", "당국 대응:", "후속 조치:"
   - 고정된 섹션명 절대 사용 금지, 반드시 뉴스 내용에 맞게 창의적으로 작성

3. 표현 스타일:
   - 객관적이고 중립적인 어조 유지
   - 사실에 기반한 명확하고 정확한 표현 사용
   - 직접 인용구를 적극 활용하여 신뢰성과 생동감 부여
   - 예: • "수백만 개 일자리 파괴하고 국가에 막대한 전략적 피해" 우려
   - 과장이나 추측보다는 확인된 사실과 공식 발언 중심

4. 글머리 기호:
   - 주요 사실/현황은 • 기호 사용
   - 순차적 내용이나 상세 설명은 1. 2. 3. 번호 사용
   - 중요한 발언이나 공식 성명은 따옴표(" ")로 강조

5. 주식 심볼 규칙:
   - 기업명 뒤에 $ 심볼과 종목 코드 표기
   - $ 심볼 앞뒤에는 반드시 공백 1칸 확보
   - 예: 테슬라 $TSLA, 애플 $AAPL, 마이크로소프트 $MSFT

6. 해시태그 추가 (필수):
   - 마지막에 뉴스와 관련된 해시태그 5-8개 추가
   - 주요 키워드, 인물명, 기업명, 정책명 등을 해시태그로 변환
   - 예: #트럼프감세안 #일론머스크 #녹색에너지 #재생에너지 #공화당 #상원법안 #세금공제

7. 이모지 선택 가이드:
   - 갈등/논란: ⚖️ ⚔️ 🔥 💥 🎯
   - 정책/정치: 🏛️ 📜 🗳️ ⚖️ 🔨
   - 경제/금융: 💰 💵 📈 📊 💸
   - 기술/혁신: 🚀 💡 🔧 🌟 ⚡
   - 기업/비즈니스: 🏢 📊 💼 🎯 🔥
   - 에너지/환경: 🌱 ⚡ 🔋 🌍 ♻️
   - 변화/발표: 💥 🚨 ⚡ 🌪️ 🎢

8. 문체와 톤:
   - 객관적이고 균형잡힌 시각으로 사실 전달
   - 갈등이나 논란은 양측 입장을 공정하게 제시
   - 숫자나 통계는 정확하고 구체적으로 표현 ("최소 4조 달러", "수십만 개")
   - 전문 용어는 한글로 풀어쓰되 정확성 유지

9. 제외할 내용:
   - 기자 정보, 연락처, 프로필
   - 광고성 메시지, 뉴스레터 구독 안내
   - 추측성이나 확인되지 않은 정보

예시 형식:
{example}

입력 데이터:
제목: {title}
URL: {url}
내용: {content}

중요한 지침:
- 제목은 명확하고 정확하게 핵심 내용 전달
- 섹션명은 뉴스 상황에 정확히 맞게 창의적으로 작성
- 직접 인용구를 적극 활용하여 신뢰성 확보
- 마지막에 관련 해시태그 반드시 포함
- 객관적이고 균형잡힌 관점으로 정보 전달
- $ 심볼 앞뒤 공백 1칸 반드시 확보

**핵심 문장 작성 원칙**:
- 사실에 기반한 정확하고 명확한 정보 전달
- 독자가 핵심 내용을 빠르게 이해할 수 있는 구조
- 공식 발언과 확인된 데이터 중심의 객관적 서술
- 인용구를 통한 신뢰성 있는 정보 제공
- 예상되는 파급효과와 영향을 사실적으로 제시
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