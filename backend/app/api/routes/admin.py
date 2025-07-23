from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
from pydantic import BaseModel

from ...core.database import User, Tenant, Device, Scan, get_db
from ...core.security import get_current_user, require_admin
from ...middleware.tenant import get_current_tenant

router = APIRouter()

# Admin Schemas
class PricingPlan(BaseModel):
    plan_type: str
    name: str
    price_monthly: float
    price_annually: float
    max_devices: int
    max_users: int
    max_scans_per_month: int
    features: List[str]
    is_active: bool = True

class SystemStats(BaseModel):
    total_users: int
    total_tenants: int
    total_devices: int
    total_scans: int
    active_subscriptions: int
    monthly_revenue: float

class UserManagement(BaseModel):
    id: int
    email: str
    full_name: str
    company_name: str
    is_active: bool
    is_admin: bool
    subscription_plan: str
    created_at: str

# Pricing Plans Storage (In production, this would be in database)
PRICING_PLANS = {
    "trial": {
        "name": "Trial",
        "price_monthly": 0,
        "price_annually": 0,
        "max_devices": 5,
        "max_users": 1,
        "max_scans_per_month": 100,
        "features": [
            "5 devices",
            "Basic scanning",
            "Email support",
            "7-day trial"
        ],
        "is_active": True
    },
    "starter": {
        "name": "Starter",
        "price_monthly": 29,
        "price_annually": 290,
        "max_devices": 50,
        "max_users": 5,
        "max_scans_per_month": 1000,
        "features": [
            "50 devices",
            "Basic vulnerability scanning",
            "Email notifications",
            "Standard support",
            "Basic reporting",
            "API access"
        ],
        "is_active": True
    },
    "professional": {
        "name": "Professional",
        "price_monthly": 99,
        "price_annually": 990,
        "max_devices": 500,
        "max_users": 25,
        "max_scans_per_month": 10000,
        "features": [
            "500 devices",
            "Advanced vulnerability scanning",
            "Real-time monitoring",
            "Priority support",
            "Advanced reporting & analytics",
            "Full API access",
            "Custom integrations",
            "Compliance templates"
        ],
        "is_active": True
    },
    "enterprise": {
        "name": "Enterprise",
        "price_monthly": 299,
        "price_annually": 2990,
        "max_devices": -1,  # Unlimited
        "max_users": -1,    # Unlimited
        "max_scans_per_month": -1,  # Unlimited
        "features": [
            "Unlimited devices",
            "Everything in Professional",
            "Dedicated account manager",
            "Custom security policies",
            "On-premise deployment",
            "SSO integration",
            "Advanced threat intelligence",
            "24/7 phone support",
            "Custom training",
            "SLA guarantees"
        ],
        "is_active": True
    }
}

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get system-wide statistics (Super Admin only)"""
    
    # Total users
    users_result = await db.execute(select(func.count(User.id)))
    total_users = users_result.scalar() or 0
    
    # Total tenants
    tenants_result = await db.execute(select(func.count(Tenant.id)))
    total_tenants = tenants_result.scalar() or 0
    
    # Total devices
    devices_result = await db.execute(select(func.count(Device.id)))
    total_devices = devices_result.scalar() or 0
    
    # Total scans
    scans_result = await db.execute(select(func.count(Scan.id)))
    total_scans = scans_result.scalar() or 0
    
    # Active subscriptions (mock data)
    active_subscriptions = total_users  # Simplified
    
    # Monthly revenue (mock calculation)
    monthly_revenue = active_subscriptions * 50  # Average $50 per user
    
    return SystemStats(
        total_users=total_users,
        total_tenants=total_tenants,
        total_devices=total_devices,
        total_scans=total_scans,
        active_subscriptions=active_subscriptions,
        monthly_revenue=monthly_revenue
    )

@router.get("/users", response_model=List[UserManagement])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (Super Admin only)"""
    
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    users = result.scalars().all()
    
    user_list = []
    for user in users:
        user_list.append(UserManagement(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            company_name=user.company_name or "",
            is_active=user.is_active,
            is_admin=user.is_admin,
            subscription_plan="trial",  # Simplified
            created_at=user.created_at.isoformat() if user.created_at else ""
        ))
    
    return user_list

@router.get("/pricing", response_model=Dict[str, Any])
async def get_pricing_plans(
    current_user: User = Depends(require_admin)
):
    """Get all pricing plans (Admin only)"""
    return PRICING_PLANS

@router.put("/pricing/{plan_type}")
async def update_pricing_plan(
    plan_type: str,
    plan_data: Dict[str, Any],
    current_user: User = Depends(require_admin)
):
    """Update pricing plan (Admin only)"""
    
    if plan_type not in PRICING_PLANS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pricing plan not found"
        )
    
    # Update pricing plan
    PRICING_PLANS[plan_type].update(plan_data)
    
    return {
        "message": f"Pricing plan '{plan_type}' updated successfully",
        "plan": PRICING_PLANS[plan_type]
    }

@router.post("/users/{user_id}/toggle-admin")
async def toggle_user_admin(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Toggle user admin status (Super Admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Toggle admin status
    user.is_admin = not user.is_admin
    await db.commit()
    
    return {
        "message": f"User admin status updated",
        "user_id": user.id,
        "is_admin": user.is_admin
    }

@router.post("/users/{user_id}/toggle-active")
async def toggle_user_active(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Toggle user active status (Super Admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Toggle active status
    user.is_active = not user.is_active
    await db.commit()
    
    return {
        "message": f"User active status updated",
        "user_id": user.id,
        "is_active": user.is_active
    }

@router.get("/tenants")
async def get_all_tenants(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all tenants (Super Admin only)"""
    
    result = await db.execute(
        select(Tenant)
        .offset(skip)
        .limit(limit)
        .order_by(Tenant.created_at.desc())
    )
    tenants = result.scalars().all()
    
    tenant_list = []
    for tenant in tenants:
        # Count users for this tenant
        users_result = await db.execute(
            select(func.count(User.id)).where(User.tenant_id == tenant.id)
        )
        user_count = users_result.scalar() or 0
        
        # Count devices for this tenant
        devices_result = await db.execute(
            select(func.count(Device.id)).where(Device.tenant_id == tenant.id)
        )
        device_count = devices_result.scalar() or 0
        
        tenant_list.append({
            "id": tenant.id,
            "name": tenant.name,
            "plan_type": tenant.plan_type,
            "user_count": user_count,
            "device_count": device_count,
            "is_active": tenant.is_active,
            "created_at": tenant.created_at.isoformat() if tenant.created_at else ""
        })
    
    return tenant_list