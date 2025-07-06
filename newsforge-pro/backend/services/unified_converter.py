"""
통합 뉴스 변환 서비스
모든 중복된 컨버터 코드를 제거하고 단일 서비스로 통합
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

# 중앙집중식 설정 import
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.api_keys import get_openai_key, get_anthropic_key, validate_api_key
from config.content_guidelines import get_content_prompt, fix_content_format, get_prompt_template

# AI 클라이언트
import openai
import anthropic


logger = logging.getLogger(__name__)


class UnifiedConverter:
    """통합 뉴스 변환 서비스 - 모든 중복 제거"""
    
    def __init__(self):
        self.supported_providers = ['openai', 'anthropic']
        logger.info("🚀 Unified Converter Service initialized")
    
    async def convert_news(
        self, 
        url: str, 
        title: str, 
        content: str, 
        provider: str = 'openai',
        user_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        뉴스를 마크다운으로 변환 (통합 메서드)
        
        Args:
            url: 뉴스 URL
            title: 제목
            content: 본문 내용
            provider: AI 제공자 ('openai' 또는 'anthropic')
            user_api_key: 사용자 제공 API 키 (선택사항)
        
        Returns:
            변환된 마크다운 및 메타데이터
        """
        start_time = datetime.now()
        conversion_id = str(uuid.uuid4())
        
        try:
            logger.info(f"🔄 Starting conversion {conversion_id} with {provider}")
            
            # 1. API 키 검증 및 가져오기
            api_key = await self._get_validated_api_key(provider, user_api_key)
            
            # 2. 콘텐츠 생성 프롬프트 준비
            prompt = get_content_prompt(
                title=title,
                description="",  # URL에서 추출된 경우 description이 없을 수 있음
                content=content
            )
            
            # 3. AI API 호출
            raw_response = await self._call_ai_api(provider, api_key, prompt)
            
            # 4. 응답 정제 및 포맷팅
            formatted_content = fix_content_format(raw_response)
            
            # 5. 메타데이터 생성
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'id': conversion_id,
                'url': url,
                'original_title': title,
                'markdown_content': formatted_content,
                'provider': provider,
                'processing_time_seconds': processing_time,
                'timestamp': datetime.now().isoformat(),
                'success': True,
                'token_usage': self._estimate_tokens(prompt, raw_response)
            }
            
            logger.info(f"✅ Conversion {conversion_id} completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"❌ Conversion {conversion_id} failed: {str(e)}")
            
            return {
                'id': conversion_id,
                'url': url,
                'original_title': title,
                'markdown_content': '',
                'provider': provider,
                'processing_time_seconds': processing_time,
                'timestamp': datetime.now().isoformat(),
                'success': False,
                'error': str(e)
            }
    
    async def _get_validated_api_key(self, provider: str, user_key: Optional[str] = None) -> str:
        """API 키 검증 및 반환"""
        if provider not in self.supported_providers:
            raise ValueError(f"Unsupported provider: {provider}")
        
        # 디버깅을 위한 로깅 추가
        logger.info(f"🔑 API Key validation - Provider: {provider}, User key provided: {user_key is not None}")
        if user_key:
            logger.info(f"🔑 User key length: {len(user_key)}, starts with: {user_key[:10]}...")
        else:
            logger.warning("🔑 No user API key provided!")
        
        try:
            if provider == 'openai':
                # user_key가 None이거나 빈 문자열인 경우 명시적으로 처리
                if not user_key or user_key.strip() == "":
                    logger.error("🔑 OpenAI user key is empty or None")
                    raise ValueError("OpenAI API key is required")
                
                validated_key = get_openai_key(user_key)
                logger.info(f"🔑 OpenAI key validated successfully: {validated_key[:10]}...")
                return validated_key
                
            elif provider == 'anthropic':
                if not user_key or user_key.strip() == "":
                    logger.error("🔑 Anthropic user key is empty or None")
                    raise ValueError("Anthropic API key is required")
                
                validated_key = get_anthropic_key(user_key)
                logger.info(f"🔑 Anthropic key validated successfully: {validated_key[:10]}...")
                return validated_key
            else:
                raise ValueError(f"Unsupported provider: {provider}")
        except ValueError as e:
            logger.error(f"❌ API key validation failed for {provider}: {str(e)}")
            raise ValueError(f"API 키와 제공업체를 설정해주세요. 상세: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected error during API key validation: {str(e)}")
            raise ValueError(f"API 키와 제공업체를 설정해주세요. 예상치 못한 오류: {str(e)}")
    
    async def _call_ai_api(self, provider: str, api_key: str, prompt: str) -> str:
        """AI API 통합 호출"""
        if provider == 'openai':
            return await self._call_openai(api_key, prompt)
        elif provider == 'anthropic':
            return await self._call_anthropic(api_key, prompt)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def _call_openai(self, api_key: str, prompt: str) -> str:
        """OpenAI API 호출"""
        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0
            )
            
            content = response.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned empty response")
            
            logger.info("✅ OpenAI API call successful")
            return content.strip()
            
        except Exception as e:
            logger.error(f"❌ OpenAI API call failed: {str(e)}")
            raise
    
    async def _call_anthropic(self, api_key: str, prompt: str) -> str:
        """Anthropic API 호출"""
        try:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            
            response = await client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0
            )
            
            content = response.content[0].text
            if not content:
                raise ValueError("Anthropic returned empty response")
            
            logger.info("✅ Anthropic API call successful")
            return content.strip()
            
        except Exception as e:
            logger.error(f"❌ Anthropic API call failed: {str(e)}")
            raise
    
    def _estimate_tokens(self, prompt: str, response: str) -> Dict[str, int]:
        """토큰 사용량 추정"""
        # 간단한 토큰 추정 (실제로는 더 정확한 계산 필요)
        prompt_tokens = len(prompt.split()) * 1.3  # 한국어 특성 고려
        response_tokens = len(response.split()) * 1.3
        
        return {
            'prompt_tokens': int(prompt_tokens),
            'completion_tokens': int(response_tokens),
            'total_tokens': int(prompt_tokens + response_tokens)
        }
    
    async def validate_api_key_async(self, provider: str, api_key: str) -> Dict[str, Any]:
        """API 키 비동기 검증"""
        try:
            # 형식 검증
            if not validate_api_key(api_key, provider):
                return {
                    'valid': False,
                    'provider': provider,
                    'error': 'Invalid API key format'
                }
            
            # 실제 API 호출 테스트
            test_prompt = "안녕하세요. API 키 테스트입니다."
            
            if provider == 'openai':
                await self._call_openai(api_key, test_prompt)
            elif provider == 'anthropic':
                await self._call_anthropic(api_key, test_prompt)
            
            return {
                'valid': True,
                'provider': provider,
                'message': 'API key is valid and working'
            }
            
        except Exception as e:
            return {
                'valid': False,
                'provider': provider,
                'error': str(e)
            }
    
    def get_supported_providers(self) -> list:
        """지원되는 AI 제공자 목록 반환"""
        return self.supported_providers.copy()
    
    def get_service_info(self) -> Dict[str, Any]:
        """서비스 정보 반환"""
        return {
            'name': 'Unified Converter Service',
            'version': '1.0.0',
            'supported_providers': self.supported_providers,
            'features': [
                'Central API key management',
                'Unified content guidelines',
                'Automatic format validation',
                'Error handling and fallback',
                'Token usage tracking'
            ],
            'status': 'active'
        }


# 전역 인스턴스 (싱글톤 패턴)
_unified_converter_instance = None


def get_unified_converter() -> UnifiedConverter:
    """통합 컨버터 인스턴스 반환 (싱글톤)"""
    global _unified_converter_instance
    if _unified_converter_instance is None:
        _unified_converter_instance = UnifiedConverter()
    return _unified_converter_instance


# 편의 함수들
async def convert_news_unified(
    url: str,
    title: str, 
    content: str,
    provider: str = 'openai',
    user_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """통합 뉴스 변환 (편의 함수)"""
    converter = get_unified_converter()
    return await converter.convert_news(url, title, content, provider, user_api_key)


async def validate_user_api_key(provider: str, api_key: str) -> Dict[str, Any]:
    """사용자 API 키 검증 (편의 함수)"""
    converter = get_unified_converter()
    return await converter.validate_api_key_async(provider, api_key) 