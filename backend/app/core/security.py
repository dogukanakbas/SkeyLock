from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .config import settings
from .database import get_db, User

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Security
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a JWT refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user."""
    from .database import Subscription, Tenant
    
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id_str = payload.get("sub")
    tenant_id = payload.get("tenant_id")
    
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID in token"
        )
    
    # Load user with tenant and subscription eagerly
    result = await db.execute(
        select(User)
        .where(User.id == user_id)
        .options(
            selectinload(User.subscription),
            selectinload(User.tenant)
        )
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Verify tenant access
    if tenant_id and user.tenant_id != tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this tenant"
        )
    
    return user


async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current authenticated admin user."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def check_subscription_limits(user: User, action: str, db: AsyncSession) -> bool:
    """Check if user's subscription allows the requested action."""
    from .database import Device
    
    if not user.subscription:
        return False
    
    subscription = user.subscription
    
    # Demo users have limited access
    if subscription.plan_type == "demo":
        if action == "scan_device":
            # Demo users can scan max 5 devices
            result = await db.execute(select(Device).where(Device.user_id == user.id))
            device_count = len(result.scalars().all())
            return device_count < 5
        elif action == "advanced_scan":
            return False
    
    # Starter plan limits
    elif subscription.plan_type == "starter":
        if action == "scan_device":
            result = await db.execute(select(Device).where(Device.user_id == user.id))
            device_count = len(result.scalars().all())
            return device_count < 50
        elif action == "api_access":
            return False
    
    # Professional and Enterprise have full access
    elif subscription.plan_type in ["professional", "enterprise"]:
        return True
    
    return False
d
ef require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def check_subscription_limits(tenant, resource_type: str, current_count: int) -> bool:
    """Check if tenant can add more resources based on their plan"""
    limits = {
        "trial": {"devices": 5, "users": 1, "scans_per_month": 100},
        "starter": {"devices": 50, "users": 5, "scans_per_month": 1000},
        "professional": {"devices": 500, "users": 25, "scans_per_month": 10000},
        "enterprise": {"devices": -1, "users": -1, "scans_per_month": -1}  # Unlimited
    }
    
    plan_limits = limits.get(tenant.plan_type, limits["trial"])
    resource_limit = plan_limits.get(resource_type, 0)
    
    # -1 means unlimited
    if resource_limit == -1:
        return True
    
    return current_count < resource_limit