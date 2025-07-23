from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List
import stripe
from datetime import datetime, timezone

from ...core.database import get_db, User, Subscription
from ...core.security import get_current_user
from ...core.config import settings

router = APIRouter()

# Stripe configuration
stripe.api_key = settings.STRIPE_SECRET_KEY


class SubscriptionPlan(BaseModel):
    name: str
    price: int
    features: List[str]
    device_limit: int
    stripe_price_id: str


class SubscriptionResponse(BaseModel):
    plan_type: str
    status: str
    current_period_start: datetime
    current_period_end: datetime
    trial_days_left: int


# Available plans
PLANS = {
    "starter": SubscriptionPlan(
        name="Starter",
        price=2900,
        features=["Up to 50 devices", "Basic scans", "Email support"],
        device_limit=50,
        stripe_price_id="price_starter_monthly"
    ),
    "professional": SubscriptionPlan(
        name="Professional", 
        price=9900,
        features=["Unlimited devices", "Advanced scans", "API access", "Priority support"],
        device_limit=-1,
        stripe_price_id="price_professional_monthly"
    ),
    "enterprise": SubscriptionPlan(
        name="Enterprise",
        price=29900,
        features=["Everything in Professional", "Multi-location", "Custom integrations", "Dedicated support"],
        device_limit=-1,
        stripe_price_id="price_enterprise_monthly"
    )
}


@router.get("/plans", response_model=List[SubscriptionPlan])
async def get_plans():
    """Get available subscription plans."""
    return list(PLANS.values())


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's subscription."""
    
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    trial_days_left = 0
    if subscription.trial_end:
        days_left = (subscription.trial_end - datetime.now(timezone.utc)).days
        trial_days_left = max(0, days_left)
    
    return SubscriptionResponse(
        plan_type=subscription.plan_type,
        status=subscription.status,
        current_period_start=subscription.current_period_start,
        current_period_end=subscription.current_period_end,
        trial_days_left=trial_days_left
    )


@router.post("/upgrade/{plan_name}")
async def upgrade_subscription(
    plan_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upgrade user's subscription."""
    
    if plan_name not in PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan"
        )
    
    # Get user's subscription
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == current_user.id)
    )
    subscription = result.scalar_one_or_none()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No subscription found"
        )
    
    try:
        # Create Stripe checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=subscription.stripe_customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': PLANS[plan_name].stripe_price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url='https://yourdomain.com/success',
            cancel_url='https://yourdomain.com/cancel',
            metadata={
                'user_id': current_user.id,
                'plan_name': plan_name
            }
        )
        
        return {"checkout_url": checkout_session.url}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Handle Stripe webhooks."""
    
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = int(session['metadata']['user_id'])
        plan_name = session['metadata']['plan_name']
        
        # Update user's subscription
        result = await db.execute(
            select(Subscription).where(Subscription.user_id == user_id)
        )
        subscription = result.scalar_one()
        
        subscription.plan_type = plan_name
        subscription.status = "active"
        subscription.stripe_subscription_id = session['subscription']
        
        await db.commit()
    
    return {"status": "success"}