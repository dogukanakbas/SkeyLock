from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from typing import Dict, Any
import stripe
from datetime import datetime, timezone

from ..celery_app import celery_app
from ..core.database import AsyncSessionLocal, Tenant, User
from ..services.stripe_service import StripeService
from ..core.config import settings

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@celery_app.task
def process_monthly_billing():
    """Process monthly billing for all tenants"""
    return asyncio.run(_process_monthly_billing_async())


async def _process_monthly_billing_async():
    """Async implementation of monthly billing"""
    async with AsyncSessionLocal() as db:
        try:
            # Get all active tenants with subscriptions
            result = await db.execute(
                select(Tenant).where(
                    Tenant.is_active == True,
                    Tenant.stripe_subscription_id.isnot(None)
                )
            )
            tenants = result.scalars().all()
            
            processed_count = 0
            failed_count = 0
            
            for tenant in tenants:
                try:
                    # Get usage data
                    usage_data = await StripeService.get_usage_record(tenant, db)
                    
                    # Report usage to Stripe (for usage-based billing)
                    if tenant.plan_type in ["professional", "enterprise"]:
                        await _report_usage_to_stripe(tenant, usage_data)
                    
                    # Check for overages and send notifications
                    await _check_usage_limits(tenant, usage_data, db)
                    
                    processed_count += 1
                    
                except Exception as e:
                    print(f"Failed to process billing for tenant {tenant.id}: {e}")
                    failed_count += 1
            
            return {
                'total_tenants': len(tenants),
                'processed': processed_count,
                'failed': failed_count
            }
            
        except Exception as e:
            raise Exception(f"Failed to process monthly billing: {str(e)}")


async def _report_usage_to_stripe(tenant: Tenant, usage_data: Dict[str, int]):
    """Report usage to Stripe for usage-based billing"""
    try:
        if not tenant.stripe_subscription_id:
            return
        
        # Get subscription from Stripe
        subscription = stripe.Subscription.retrieve(tenant.stripe_subscription_id)
        
        # Report device usage
        if usage_data['devices'] > 0:
            stripe.SubscriptionItem.create_usage_record(
                subscription.items.data[0].id,  # Assuming first item is device usage
                quantity=usage_data['devices'],
                timestamp=int(datetime.now(timezone.utc).timestamp())
            )
        
        # Report scan usage
        if usage_data['scans_this_month'] > 0:
            # Find scan usage item (if exists)
            for item in subscription.items.data:
                if 'scan' in item.price.nickname.lower():
                    stripe.SubscriptionItem.create_usage_record(
                        item.id,
                        quantity=usage_data['scans_this_month'],
                        timestamp=int(datetime.now(timezone.utc).timestamp())
                    )
                    break
        
    except Exception as e:
        print(f"Failed to report usage to Stripe for tenant {tenant.id}: {e}")


async def _check_usage_limits(tenant: Tenant, usage_data: Dict[str, int], db: AsyncSession):
    """Check if tenant is approaching or exceeding limits"""
    from ..tasks.notification_tasks import send_usage_warning
    
    # Check device limit
    device_usage_percent = (usage_data['devices'] / tenant.max_devices) * 100
    if device_usage_percent >= 90:
        send_usage_warning.delay(
            tenant.id,
            'devices',
            usage_data['devices'],
            tenant.max_devices
        )
    
    # Check scan limit
    scan_usage_percent = (usage_data['scans_this_month'] / tenant.max_scans_per_month) * 100
    if scan_usage_percent >= 90:
        send_usage_warning.delay(
            tenant.id,
            'scans',
            usage_data['scans_this_month'],
            tenant.max_scans_per_month
        )


@celery_app.task
def send_usage_warning(tenant_id: str, resource_type: str, current_usage: int, limit: int):
    """Send usage warning to tenant"""
    return asyncio.run(_send_usage_warning_async(tenant_id, resource_type, current_usage, limit))


async def _send_usage_warning_async(tenant_id: str, resource_type: str, current_usage: int, limit: int):
    """Async implementation of usage warning"""
    async with AsyncSessionLocal() as db:
        try:
            # Get tenant and users
            tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = tenant_result.scalar_one_or_none()
            
            if not tenant:
                return
            
            user_result = await db.execute(select(User).where(User.tenant_id == tenant_id))
            users = user_result.scalars().all()
            
            # Send warning email
            from ..tasks.notification_tasks import _send_email
            
            usage_percent = (current_usage / limit) * 100
            
            for user in users:
                await _send_email(
                    to_email=user.email,
                    subject=f"⚠️ Usage Warning - {tenant.name}",
                    html_content=_generate_usage_warning_html(
                        tenant.name, resource_type, current_usage, limit, usage_percent
                    )
                )
            
            return {'warnings_sent': len(users)}
            
        except Exception as e:
            raise Exception(f"Failed to send usage warning: {str(e)}")


def _generate_usage_warning_html(tenant_name: str, resource_type: str, current: int, limit: int, percent: float) -> str:
    """Generate HTML for usage warning email"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="background-color: #ff9800; color: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; text-align: center;">
                <h1 style="margin: 0;">⚠️ Usage Warning</h1>
            </div>
            
            <h2 style="color: #333; margin-bottom: 15px;">{tenant_name}</h2>
            
            <div style="background-color: #fff3cd; padding: 20px; border-radius: 6px; border-left: 4px solid #ff9800; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #856404;">You're approaching your {resource_type} limit</h3>
                <p style="color: #856404; margin-bottom: 10px;">
                    Current usage: <strong>{current} / {limit}</strong> ({percent:.1f}%)
                </p>
                <div style="background-color: #e2e3e5; border-radius: 10px; height: 20px; margin: 10px 0;">
                    <div style="background-color: #ff9800; height: 20px; border-radius: 10px; width: {min(percent, 100)}%;"></div>
                </div>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h4>What happens when you reach the limit?</h4>
                <ul>
                    <li>New {resource_type} will be blocked</li>
                    <li>Existing functionality will continue to work</li>
                    <li>You'll receive upgrade recommendations</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://app.yourdomain.com/subscription" style="background-color: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-right: 10px;">
                    Upgrade Plan
                </a>
                <a href="https://app.yourdomain.com/dashboard" style="background-color: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Dashboard
                </a>
            </div>
        </div>
    </body>
    </html>
    """


@celery_app.task
def process_failed_payments():
    """Process failed payments and send notifications"""
    return asyncio.run(_process_failed_payments_async())


async def _process_failed_payments_async():
    """Async implementation of failed payment processing"""
    try:
        # Get failed invoices from Stripe
        failed_invoices = stripe.Invoice.list(
            status='open',
            limit=100
        )
        
        processed_count = 0
        
        for invoice in failed_invoices.data:
            try:
                # Get customer and tenant info
                customer = stripe.Customer.retrieve(invoice.customer)
                tenant_id = customer.metadata.get('tenant_id')
                
                if tenant_id:
                    # Send payment failure notification
                    await _send_payment_failure_notification(tenant_id, invoice)
                    processed_count += 1
                    
            except Exception as e:
                print(f"Failed to process failed payment for invoice {invoice.id}: {e}")
        
        return {
            'failed_invoices': len(failed_invoices.data),
            'processed': processed_count
        }
        
    except Exception as e:
        raise Exception(f"Failed to process failed payments: {str(e)}")


async def _send_payment_failure_notification(tenant_id: str, invoice):
    """Send payment failure notification"""
    async with AsyncSessionLocal() as db:
        try:
            # Get tenant and users
            tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = tenant_result.scalar_one_or_none()
            
            if not tenant:
                return
            
            user_result = await db.execute(select(User).where(User.tenant_id == tenant_id))
            users = user_result.scalars().all()
            
            # Send payment failure email
            from ..tasks.notification_tasks import _send_email
            
            for user in users:
                await _send_email(
                    to_email=user.email,
                    subject=f"💳 Payment Failed - {tenant.name}",
                    html_content=_generate_payment_failure_html(tenant.name, invoice)
                )
            
        except Exception as e:
            print(f"Failed to send payment failure notification: {e}")


def _generate_payment_failure_html(tenant_name: str, invoice) -> str:
    """Generate HTML for payment failure email"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; text-align: center;">
                <h1 style="margin: 0;">💳 Payment Failed</h1>
            </div>
            
            <h2 style="color: #333; margin-bottom: 15px;">{tenant_name}</h2>
            
            <div style="background-color: #f8d7da; padding: 20px; border-radius: 6px; border-left: 4px solid #dc3545; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #721c24;">Payment could not be processed</h3>
                <p style="color: #721c24; margin-bottom: 10px;">
                    Amount: <strong>${invoice.amount_due / 100:.2f}</strong>
                </p>
                <p style="color: #721c24; margin-bottom: 0;">
                    Due Date: <strong>{datetime.fromtimestamp(invoice.due_date).strftime('%B %d, %Y') if invoice.due_date else 'Immediately'}</strong>
                </p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h4>What you need to do:</h4>
                <ol>
                    <li>Update your payment method</li>
                    <li>Ensure sufficient funds are available</li>
                    <li>Contact support if you need assistance</li>
                </ol>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://app.yourdomain.com/billing" style="background-color: #dc3545; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-right: 10px;">
                    Update Payment Method
                </a>
                <a href="https://yourdomain.com/support" style="background-color: #6c757d; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    Contact Support
                </a>
            </div>
        </div>
    </body>
    </html>
    """