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
from converters.mock_converter import MockConverter

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
        """사용자 API 키로 변환기 생성"""
        
        # 사용자가 API 키를 제공한 경우 우선 사용
        if api_key and api_provider:
            try:
                if api_provider == "openai":
                    # 사용자 API 키로 OpenAI 변환기 생성
                    import os
                    original_key = os.getenv('OPENAI_API_KEY')
                    os.environ['OPENAI_API_KEY'] = api_key
                    try:
                        converter = OpenAIConverter()
                        logger.info(f"✅ 사용자 OpenAI API 키로 변환기 생성 완료")
                        return converter
                    finally:
                        # 원래 키 복원
                        if original_key:
                            os.environ['OPENAI_API_KEY'] = original_key
                        else:
                            os.environ.pop('OPENAI_API_KEY', None)
                            
                elif api_provider == "anthropic":
                    # 사용자 API 키로 Anthropic 변환기 생성
                    import os
                    original_key = os.getenv('ANTHROPIC_API_KEY')
                    os.environ['ANTHROPIC_API_KEY'] = api_key
                    try:
                        converter = AnthropicConverter()
                        logger.info(f"✅ 사용자 Anthropic API 키로 변환기 생성 완료")
                        return converter
                    finally:
                        # 원래 키 복원
                        if original_key:
                            os.environ['ANTHROPIC_API_KEY'] = original_key
                        else:
                            os.environ.pop('ANTHROPIC_API_KEY', None)
                            
            except Exception as e:
                logger.error(f"사용자 API 키로 변환기 생성 실패: {str(e)}")
                # 실패 시 기본 변환기 사용으로 폴백
        
        # 기본 변환기 선택 로직
        return self._select_converter(converter_type)
    
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