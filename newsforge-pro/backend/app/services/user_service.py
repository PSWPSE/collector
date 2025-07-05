"""
NewsForge Pro 사용자 서비스
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from ..schemas.conversion import (
    UsageStats, 
    ConversionHistory, 
    ConversionHistoryResponse
)

class UserService:
    """사용자 관리 서비스"""
    
    def __init__(self):
        # 임시 메모리 저장소 (나중에 데이터베이스로 교체)
        self.user_store = {}
        self.history_store = {}
        self.usage_store = {}
    
    async def initialize(self):
        """서비스 초기화"""
        print("🚀 UserService 초기화 중...")
        
        # 데이터베이스 연결 등 (나중에 구현)
        # await self.db.connect()
        
        print("✅ UserService 초기화 완료")
    
    async def cleanup(self):
        """서비스 정리"""
        print("🧹 UserService 정리 중...")
        
        # 데이터베이스 연결 종료 등
        # await self.db.disconnect()
        
        print("✅ UserService 정리 완료")
    
    async def get_user_info(self, user_id: int) -> Optional[Dict]:
        """사용자 정보 조회"""
        return self.user_store.get(user_id)
    
    async def increment_usage(self, user_id: int):
        """사용량 증가"""
        
        today = datetime.now().date()
        this_month = datetime.now().replace(day=1).date()
        
        if user_id not in self.usage_store:
            self.usage_store[user_id] = {
                "daily": {},
                "monthly": {},
                "total": 0
            }
        
        user_usage = self.usage_store[user_id]
        
        # 일일 사용량
        daily_key = str(today)
        user_usage["daily"][daily_key] = user_usage["daily"].get(daily_key, 0) + 1
        
        # 월간 사용량
        monthly_key = str(this_month)
        user_usage["monthly"][monthly_key] = user_usage["monthly"].get(monthly_key, 0) + 1
        
        # 총 사용량
        user_usage["total"] = user_usage["total"] + 1
    
    async def get_usage_stats(self, user_id: int) -> Dict:
        """사용량 통계 조회"""
        
        today = datetime.now().date()
        this_month = datetime.now().replace(day=1).date()
        
        usage_data = self.usage_store.get(user_id, {
            "daily": {},
            "monthly": {},
            "total": 0
        })
        
        # 현재 사용량
        daily_usage = usage_data["daily"].get(str(today), 0)
        monthly_usage = usage_data["monthly"].get(str(this_month), 0)
        total_usage = usage_data["total"]
        
        # 사용자 정보 (임시)
        user_info = await self.get_user_info(user_id) or {
            "plan": "free",
            "created_at": datetime.now().isoformat()
        }
        
        plan_type = user_info.get("plan", "free")
        
        # 플랜별 제한
        limits = {
            "free": {"daily": 10, "monthly": 100},
            "premium": {"daily": None, "monthly": None}
        }
        
        plan_limits = limits.get(plan_type, limits["free"])
        
        return {
            "user_id": user_id,
            "plan_type": plan_type,
            "daily_usage": daily_usage,
            "daily_limit": plan_limits["daily"],
            "monthly_usage": monthly_usage,
            "monthly_limit": plan_limits["monthly"],
            "total_usage": total_usage,
            "next_reset": self._get_next_reset_time(),
            "can_use": (
                daily_usage < plan_limits["daily"] 
                if plan_limits["daily"] else True
            )
        }
    
    async def add_conversion_history(
        self, 
        user_id: int,
        task_id: str,
        url: str,
        title: str,
        platforms: List[str],
        status: str,
        processing_time: Optional[float] = None
    ):
        """변환 히스토리 추가"""
        
        if user_id not in self.history_store:
            self.history_store[user_id] = []
        
        history_item = {
            "id": task_id,
            "url": url,
            "title": title,
            "platforms": platforms,
            "status": status,
            "created_at": datetime.now().isoformat(),
            "processing_time": processing_time
        }
        
        # 최신 순으로 삽입
        self.history_store[user_id].insert(0, history_item)
        
        # 최대 100개까지만 보관
        if len(self.history_store[user_id]) > 100:
            self.history_store[user_id] = self.history_store[user_id][:100]
    
    async def get_conversion_history(
        self, 
        user_id: int,
        limit: int = 20,
        offset: int = 0
    ) -> ConversionHistoryResponse:
        """변환 히스토리 조회"""
        
        user_history = self.history_store.get(user_id, [])
        
        # 페이지네이션
        total = len(user_history)
        items_slice = user_history[offset:offset + limit]
        
        # ConversionHistory 객체로 변환
        history_items = [
            ConversionHistory(**item) for item in items_slice
        ]
        
        return ConversionHistoryResponse(
            total=total,
            items=history_items,
            has_more=offset + limit < total
        )
    
    async def get_user_dashboard_stats(self, user_id: int) -> Dict:
        """사용자 대시보드 통계"""
        
        # 사용량 통계
        usage_stats = await self.get_usage_stats(user_id)
        
        # 히스토리 통계
        user_history = self.history_store.get(user_id, [])
        
        # 최근 7일 사용량
        recent_usage = await self._get_recent_usage(user_id, days=7)
        
        # 플랫폼별 사용량
        platform_stats = await self._get_platform_stats(user_id)
        
        # 성공률 계산
        success_rate = await self._calculate_success_rate(user_id)
        
        return {
            "user_id": user_id,
            "usage_stats": usage_stats,
            "total_conversions": len(user_history),
            "recent_usage": recent_usage,
            "platform_stats": platform_stats,
            "success_rate": success_rate,
            "last_conversion": user_history[0]["created_at"] if user_history else None
        }
    
    async def _get_recent_usage(self, user_id: int, days: int = 7) -> List[Dict]:
        """최근 N일간 사용량"""
        
        usage_data = self.usage_store.get(user_id, {"daily": {}})
        recent_usage = []
        
        for i in range(days):
            date = datetime.now().date() - timedelta(days=i)
            date_str = str(date)
            count = usage_data["daily"].get(date_str, 0)
            
            recent_usage.append({
                "date": date_str,
                "count": count
            })
        
        return list(reversed(recent_usage))
    
    async def _get_platform_stats(self, user_id: int) -> Dict[str, int]:
        """플랫폼별 사용량 통계"""
        
        user_history = self.history_store.get(user_id, [])
        platform_counts = {}
        
        for item in user_history:
            for platform in item.get("platforms", []):
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
        
        return platform_counts
    
    async def _calculate_success_rate(self, user_id: int) -> float:
        """성공률 계산"""
        
        user_history = self.history_store.get(user_id, [])
        
        if not user_history:
            return 0.0
        
        successful = sum(1 for item in user_history if item["status"] == "completed")
        total = len(user_history)
        
        return round((successful / total) * 100, 2)
    
    def _get_next_reset_time(self) -> str:
        """다음 리셋 시간 (일일)"""
        
        now = datetime.now()
        next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_reset.isoformat()
    
    async def update_user_plan(self, user_id: int, plan: str):
        """사용자 플랜 업데이트"""
        
        if user_id not in self.user_store:
            self.user_store[user_id] = {}
        
        self.user_store[user_id]["plan"] = plan
        self.user_store[user_id]["plan_updated_at"] = datetime.now().isoformat()
    
    async def get_user_subscription_info(self, user_id: int) -> Dict:
        """사용자 구독 정보"""
        
        user_info = self.user_store.get(user_id, {})
        
        return {
            "user_id": user_id,
            "plan": user_info.get("plan", "free"),
            "plan_updated_at": user_info.get("plan_updated_at"),
            "subscription_status": "active" if user_info.get("plan") == "premium" else "inactive",
            "next_billing_date": None,  # 나중에 구현
            "billing_amount": 9.99 if user_info.get("plan") == "premium" else 0
        }
    
    async def cleanup_old_data(self):
        """오래된 데이터 정리"""
        
        # 30일 이전 사용량 데이터 삭제
        cutoff_date = datetime.now().date() - timedelta(days=30)
        
        for user_id in self.usage_store:
            user_data = self.usage_store[user_id]
            
            # 오래된 일일 데이터 삭제
            old_daily_keys = [
                key for key in user_data["daily"].keys() 
                if datetime.strptime(key, "%Y-%m-%d").date() < cutoff_date
            ]
            
            for key in old_daily_keys:
                del user_data["daily"][key]
        
        # 90일 이전 히스토리 삭제
        cutoff_datetime = datetime.now() - timedelta(days=90)
        
        for user_id in self.history_store:
            user_history = self.history_store[user_id]
            
            # 오래된 히스토리 필터링
            self.history_store[user_id] = [
                item for item in user_history
                if datetime.fromisoformat(item["created_at"]) > cutoff_datetime
            ] 