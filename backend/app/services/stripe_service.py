import stripe
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from ..core.config import settings
from ..core.database import Tenant, User, Subscription

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:
    """Production-ready Stripe integration"""
    
    @staticmethod
    async def create_customer(tenant: Tenant, user: User) -> str:
        """Create Stripe customer for tenant"""
        try:
            customer = stripe.Customer.create(
                email=user.email,
                name=user.full_name,
                metadata={
                    "tenant_id": tenant.id,
                    "user_id": str(user.id),
                    "tenant_name": tenant.name
                }
            )
            return customer.id
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create Stripe customer: {str(e)}")
    
    @staticmethod
    async def create_subscription(
        customer_id: str, 
        price_id: str, 
        tenant: Tenant,
        trial_days: int = 7
    ) -> Dict[str, Any]:
        """Create Stripe subscription"""
        try:
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                trial_period_days=trial_days,
                metadata={
                    "tenant_id": tenant.id,
                    "tenant_name": tenant.name
                },
                expand=["latest_invoice.payment_intent"]
            )
            return subscription
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create subscription: {str(e)}")
    
    @staticmethod
    async def create_checkout_session(
        tenant: Tenant,
        user: User,
        plan_type: str,
        success_url: str,
        cancel_url: str
    ) -> str:
        """Create Stripe Checkout session"""
        
        # Price mapping
        price_mapping = {
            "starter": settings.STRIPE_STARTER_PRICE_ID,
            "professional": settings.STRIPE_PROFESSIONAL_PRICE_ID,
            "enterprise": settings.STRIPE_ENTERPRISE_PRICE_ID
        }
        
        price_id = price_mapping.get(plan_type)
        if not price_id:
            raise Exception(f"Invalid plan type: {plan_type}")
        
        try:
            session = stripe.checkout.Session.create(
                customer_email=user.email,
                payment_method_types=["card"],
                line_items=[{
                    "price": price_id,
                    "quantity": 1,
                }],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "tenant_id": tenant.id,
                    "user_id": str(user.id),
                    "plan_type": plan_type
                },
                subscription_data={
                    "trial_period_days": 7,
                    "metadata": {
                        "tenant_id": tenant.id,
                        "plan_type": plan_type
                    }
                }
            )
            return session.url
        except stripe.error.StripeError as e:
            raise Exception(f"Failed to create checkout session: {str(e)}")
    
    @staticmethod
    async def handle_webhook(payload: str, sig_header: str) -> Dict[str, Any]:
        """Handle Stripe webhook events"""
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event
        except ValueError:
            raise Exception("Invalid payload")
        except stripe.error.SignatureVerificationError:
            raise Exception("Invalid signature")
    
    @staticmethod
    async def update_tenant_subscription(
        db: AsyncSession,
        tenant_id: str,
        stripe_subscription: Dict[str, Any]
    ):
        """Update tenant subscription from Stripe data"""
        result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return
        
        # Update tenant based on subscription
        plan_type = stripe_subscription.get("metadata", {}).get("plan_type", "starter")
        
        # Set limits based on plan
        if plan_type == "starter":
            tenant.max_devices = 50
            tenant.max_users = 5
            tenant.max_scans_per_month = 1000
        elif plan_type == "professional":
            tenant.max_devices = 500
            tenant.max_users = 25
            tenant.max_scans_per_month = 10000
        elif plan_type == "enterprise":
            tenant.max_devices = 10000
            tenant.max_users = 100
            tenant.max_scans_per_month = 100000
        
        tenant.plan_type = plan_type
        tenant.status = "active"
        tenant.stripe_subscription_id = stripe_subscription["id"]
        
        await db.commit()
    
    @staticmethod
    async def cancel_subscription(subscription_id: str) -> bool:
        """Cancel Stripe subscription"""
        try:
            stripe.Subscription.delete(subscription_id)
            return True
        except stripe.error.StripeError:
            return False
    
    @staticmethod
    async def get_usage_record(tenant: Tenant, db: AsyncSession) -> Dict[str, int]:
        """Get current usage for tenant"""
        from ..core.database import Device, Scan
        
        # Count devices
        device_result = await db.execute(
            select(Device).where(Device.tenant_id == tenant.id)
        )
        device_count = len(device_result.scalars().all())
        
        # Count users
        user_result = await db.execute(
            select(User).where(User.tenant_id == tenant.id)
        )
        user_count = len(user_result.scalars().all())
        
        # Count scans this month
        from sqlalchemy import func, extract
        current_month = datetime.now(timezone.utc).month
        current_year = datetime.now(timezone.utc).year
        
        scan_result = await db.execute(
            select(func.count(Scan.id)).where(
                Scan.tenant_id == tenant.id,
                extract('month', Scan.started_at) == current_month,
                extract('year', Scan.started_at) == current_year
            )
        )
        scan_count = scan_result.scalar() or 0
        
        return {
            "devices": device_count,
            "users": user_count,
            "scans_this_month": scan_count
        }