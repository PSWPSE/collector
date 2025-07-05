"""
NewsForge Pro 사용량 제한 서비스
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
import time

class RateLimiter:
    """사용량 제한 관리"""
    
    def __init__(self):
        # 임시 메모리 저장소 (나중에 Redis로 교체)
        self.usage_store = {}
        
        # 플랜별 제한 설정
        self.plan_limits = {
            "free": {
                "daily_limit": 10,
                "monthly_limit": 100,
                "concurrent_limit": 1
            },
            "premium": {
                "daily_limit": None,  # 무제한
                "monthly_limit": None,  # 무제한
                "concurrent_limit": 5
            }
        }
    
    async def check_user_limit(self, user_id: int, user_plan: str) -> Dict:
        """
        사용자 사용량 제한 확인
        
        Args:
            user_id: 사용자 ID
            user_plan: 사용자 플랜 (free, premium)
            
        Returns:
            제한 확인 결과 딕셔너리
        """
        
        plan_config = self.plan_limits.get(user_plan, self.plan_limits["free"])
        
        # 현재 사용량 조회
        usage = await self._get_user_usage(user_id)
        
        # 일일 제한 확인
        daily_limit = plan_config["daily_limit"]
        if daily_limit and usage["daily_count"] >= daily_limit:
            return {
                "allowed": False,
                "reason": "daily_limit_exceeded",
                "current_usage": usage["daily_count"],
                "limit": daily_limit,
                "reset_time": self._get_next_reset_time("daily")
            }
        
        # 월간 제한 확인
        monthly_limit = plan_config["monthly_limit"]
        if monthly_limit and usage["monthly_count"] >= monthly_limit:
            return {
                "allowed": False,
                "reason": "monthly_limit_exceeded",
                "current_usage": usage["monthly_count"],
                "limit": monthly_limit,
                "reset_time": self._get_next_reset_time("monthly")
            }
        
        # 동시 작업 제한 확인
        concurrent_limit = plan_config["concurrent_limit"]
        if usage["concurrent_count"] >= concurrent_limit:
            return {
                "allowed": False,
                "reason": "concurrent_limit_exceeded",
                "current_usage": usage["concurrent_count"],
                "limit": concurrent_limit,
                "message": "진행 중인 작업이 완료된 후 다시 시도해주세요"
            }
        
        return {
            "allowed": True,
            "current_usage": usage["daily_count"],
            "limit": daily_limit,
            "remaining": daily_limit - usage["daily_count"] if daily_limit else "unlimited"
        }
    
    async def _get_user_usage(self, user_id: int) -> Dict:
        """사용자 사용량 조회"""
        
        today = datetime.now().date()
        this_month = datetime.now().replace(day=1).date()
        
        user_key = f"user_{user_id}"
        if user_key not in self.usage_store:
            self.usage_store[user_key] = {
                "daily": {},
                "monthly": {},
                "concurrent": 0
            }
        
        user_data = self.usage_store[user_key]
        
        # 일일 사용량
        daily_count = user_data["daily"].get(str(today), 0)
        
        # 월간 사용량
        monthly_count = user_data["monthly"].get(str(this_month), 0)
        
        # 동시 작업 수
        concurrent_count = user_data["concurrent"]
        
        return {
            "daily_count": daily_count,
            "monthly_count": monthly_count,
            "concurrent_count": concurrent_count
        }
    
    async def increment_usage(self, user_id: int):
        """사용량 증가"""
        
        today = datetime.now().date()
        this_month = datetime.now().replace(day=1).date()
        
        user_key = f"user_{user_id}"
        if user_key not in self.usage_store:
            self.usage_store[user_key] = {
                "daily": {},
                "monthly": {},
                "concurrent": 0
            }
        
        user_data = self.usage_store[user_key]
        
        # 일일 사용량 증가
        daily_key = str(today)
        user_data["daily"][daily_key] = user_data["daily"].get(daily_key, 0) + 1
        
        # 월간 사용량 증가
        monthly_key = str(this_month)
        user_data["monthly"][monthly_key] = user_data["monthly"].get(monthly_key, 0) + 1
        
        # 동시 작업 수 증가
        user_data["concurrent"] = user_data["concurrent"] + 1
    
    async def decrement_concurrent(self, user_id: int):
        """동시 작업 수 감소"""
        
        user_key = f"user_{user_id}"
        if user_key in self.usage_store:
            user_data = self.usage_store[user_key]
            user_data["concurrent"] = max(0, user_data["concurrent"] - 1)
    
    def _get_next_reset_time(self, period: str) -> str:
        """다음 리셋 시간 계산"""
        
        now = datetime.now()
        
        if period == "daily":
            next_reset = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        elif period == "monthly":
            if now.month == 12:
                next_reset = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                next_reset = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_reset = now + timedelta(hours=1)
        
        return next_reset.isoformat()
    
    async def get_usage_stats(self, user_id: int, user_plan: str) -> Dict:
        """사용량 통계 조회"""
        
        plan_config = self.plan_limits.get(user_plan, self.plan_limits["free"])
        usage = await self._get_user_usage(user_id)
        
        return {
            "user_id": user_id,
            "plan_type": user_plan,
            "daily_usage": usage["daily_count"],
            "daily_limit": plan_config["daily_limit"],
            "monthly_usage": usage["monthly_count"],
            "monthly_limit": plan_config["monthly_limit"],
            "concurrent_usage": usage["concurrent_count"],
            "concurrent_limit": plan_config["concurrent_limit"],
            "next_reset": self._get_next_reset_time("daily"),
            "can_use": usage["daily_count"] < plan_config["daily_limit"] if plan_config["daily_limit"] else True
        }
    
    async def cleanup_old_data(self):
        """오래된 사용량 데이터 정리"""
        
        # 7일 이전 데이터 삭제
        cutoff_date = datetime.now().date() - timedelta(days=7)
        
        for user_key in self.usage_store:
            user_data = self.usage_store[user_key]
            
            # 오래된 일일 데이터 삭제
            old_daily_keys = [
                key for key in user_data["daily"].keys() 
                if datetime.strptime(key, "%Y-%m-%d").date() < cutoff_date
            ]
            
            for key in old_daily_keys:
                del user_data["daily"][key] 