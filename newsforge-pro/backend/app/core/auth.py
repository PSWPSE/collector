"""
NewsForge Pro 인증 모듈
"""

from typing import Optional, Dict
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .exceptions import AuthenticationException

security = HTTPBearer()

# 임시 모의 사용자 데이터 (나중에 데이터베이스로 교체)
MOCK_USERS = {
    "test_token_123": {
        "id": 1,
        "email": "test@newsforge.pro",
        "name": "테스트 사용자",
        "plan": "free",
        "is_active": True
    },
    "premium_token_456": {
        "id": 2,
        "email": "premium@newsforge.pro", 
        "name": "프리미엄 사용자",
        "plan": "premium",
        "is_active": True
    }
}

def verify_token(token: str) -> Optional[Dict]:
    """
    토큰 검증 (임시 구현)
    
    Args:
        token: Bearer 토큰
        
    Returns:
        사용자 정보 또는 None
    """
    # 임시: 하드코딩된 토큰 확인
    return MOCK_USERS.get(token)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict:
    """
    현재 인증된 사용자 정보 반환
    
    Returns:
        사용자 정보 딕셔너리
        
    Raises:
        HTTPException: 인증 실패 시
    """
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증 토큰이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = verify_token(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.get("is_active", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="비활성화된 사용자입니다"
        )
    
    return user

async def get_current_active_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    활성 사용자만 허용
    """
    if not current_user.get("is_active"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="비활성화된 사용자입니다"
        )
    return current_user

async def get_premium_user(
    current_user: Dict = Depends(get_current_user)
) -> Dict:
    """
    프리미엄 사용자만 허용
    """
    if current_user.get("plan") != "premium":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="프리미엄 계정이 필요한 기능입니다"
        )
    return current_user

def create_access_token(user_data: Dict) -> str:
    """
    액세스 토큰 생성 (임시 구현)
    
    Args:
        user_data: 사용자 정보
        
    Returns:
        액세스 토큰
    """
    # 임시: 사용자 ID 기반 간단한 토큰
    return f"token_{user_data['id']}_{user_data['email'].split('@')[0]}"

def create_mock_user(email: str, plan: str = "free") -> Dict:
    """
    테스트용 모의 사용자 생성
    
    Args:
        email: 이메일
        plan: 요금제 (free, premium)
        
    Returns:
        사용자 정보
    """
    user_id = len(MOCK_USERS) + 1
    user_data = {
        "id": user_id,
        "email": email,
        "name": f"사용자{user_id}",
        "plan": plan,
        "is_active": True
    }
    
    token = create_access_token(user_data)
    MOCK_USERS[token] = user_data
    
    return {"user": user_data, "token": token} 