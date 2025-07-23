from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta, timezone
import stripe

from ...core.database import get_db, User, Subscription
from ...core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token,
    verify_token,
    get_current_user
)
from ...core.config import settings

router = APIRouter()

# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY


# Pydantic models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    company_name: str
    phone: str = None
    job_title: str = None
    company_size: str = None  # "1-10", "11-50", "51-200", "201-1000", "1000+"
    industry: str = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    subscription_plan: str
    subscription_status: str
    trial_days_left: int


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user with 7-day trial."""
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        company_name=user_data.company_name,
        phone=user_data.phone,
        job_title=user_data.job_title,
        company_size=user_data.company_size,
        industry=user_data.industry
    )
    
    db.add(user)
    await db.flush()  # Get user ID
    
    # Create Stripe customer
    try:
        stripe_customer = stripe.Customer.create(
            email=user_data.email,
            name=user_data.full_name,
            metadata={"user_id": user.id}
        )
    except Exception as e:
        # For development, continue without Stripe
        stripe_customer = None
        print(f"Stripe error (continuing without): {e}")
    
    # Create trial subscription
    trial_end = datetime.now(timezone.utc) + timedelta(days=settings.DEMO_DAYS)
    subscription = Subscription(
        user_id=user.id,
        plan_type="demo",
        status="trial",
        stripe_customer_id=stripe_customer.id if stripe_customer else None,
        current_period_start=datetime.now(timezone.utc),
        current_period_end=trial_end,
        trial_end=trial_end
    )
    
    db.add(subscription)
    await db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens."""
    
    # Find user
    result = await db.execute(select(User).where(User.email == user_data.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    
    payload = verify_token(refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user information."""
    
    # Get subscription info
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    
    trial_days_left = 0
    if subscription and subscription.trial_end:
        # Convert trial_end to UTC timezone for comparison
        trial_end_utc = subscription.trial_end.replace(tzinfo=timezone.utc)
        days_left = (trial_end_utc - datetime.now(timezone.utc)).days
        trial_days_left = max(0, days_left)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        is_admin=current_user.is_admin,
        subscription_plan=subscription.plan_type if subscription else "none",
        subscription_status=subscription.status if subscription else "none",
        trial_days_left=trial_days_left
    )