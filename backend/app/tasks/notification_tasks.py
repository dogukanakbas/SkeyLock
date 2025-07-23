from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from typing import List, Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..celery_app import celery_app
from ..core.database import AsyncSessionLocal, Tenant, User, Device, Scan
from ..core.config import settings


@celery_app.task
def send_daily_reports():
    """Send daily security reports to all tenants"""
    return asyncio.run(_send_daily_reports_async())


async def _send_daily_reports_async():
    """Async implementation of daily reports"""
    async with AsyncSessionLocal() as db:
        try:
            # Get all active tenants
            result = await db.execute(
                select(Tenant).where(Tenant.is_active == True)
            )
            tenants = result.scalars().all()
            
            reports_sent = 0
            
            for tenant in tenants:
                # Generate report for tenant
                report_data = await _generate_tenant_report(tenant, db)
                
                # Send email to tenant users
                await _send_report_email(tenant, report_data, db)
                reports_sent += 1
            
            return {
                'total_tenants': len(tenants),
                'reports_sent': reports_sent
            }
            
        except Exception as e:
            raise Exception(f"Failed to send daily reports: {str(e)}")


async def _generate_tenant_report(tenant: Tenant, db: AsyncSession) -> Dict[str, Any]:
    """Generate security report for tenant"""
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Get data for last 24 hours
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    # Count devices
    device_result = await db.execute(
        select(func.count(Device.id)).where(Device.tenant_id == tenant.id)
    )
    total_devices = device_result.scalar() or 0
    
    # Count active devices
    active_device_result = await db.execute(
        select(func.count(Device.id)).where(
            Device.tenant_id == tenant.id,
            Device.is_active == True
        )
    )
    active_devices = active_device_result.scalar() or 0
    
    # Count scans in last 24h
    scan_result = await db.execute(
        select(func.count(Scan.id)).where(
            Scan.tenant_id == tenant.id,
            Scan.started_at >= yesterday
        )
    )
    scans_24h = scan_result.scalar() or 0
    
    # Get high-risk devices
    high_risk_result = await db.execute(
        select(Device).where(
            Device.tenant_id == tenant.id,
            Device.risk_score >= 70
        ).limit(5)
    )
    high_risk_devices = high_risk_result.scalars().all()
    
    return {
        'tenant_name': tenant.name,
        'total_devices': total_devices,
        'active_devices': active_devices,
        'scans_24h': scans_24h,
        'high_risk_devices': [
            {
                'hostname': device.hostname or device.ip_address,
                'ip_address': device.ip_address,
                'risk_score': device.risk_score
            }
            for device in high_risk_devices
        ]
    }


async def _send_report_email(tenant: Tenant, report_data: Dict[str, Any], db: AsyncSession):
    """Send report email to tenant users"""
    try:
        # Get tenant users
        result = await db.execute(
            select(User).where(User.tenant_id == tenant.id)
        )
        users = result.scalars().all()
        
        for user in users:
            await _send_email(
                to_email=user.email,
                subject=f"Daily Security Report - {tenant.name}",
                html_content=_generate_report_html(report_data)
            )
            
    except Exception as e:
        print(f"Failed to send report email to tenant {tenant.id}: {e}")


def _generate_report_html(report_data: Dict[str, Any]) -> str:
    """Generate HTML email content for report"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #1976d2; margin-bottom: 20px;">Daily Security Report</h1>
            <h2 style="color: #333; margin-bottom: 15px;">{report_data['tenant_name']}</h2>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 6px; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #495057;">Summary</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin-bottom: 10px;">📱 <strong>Total Devices:</strong> {report_data['total_devices']}</li>
                    <li style="margin-bottom: 10px;">✅ <strong>Active Devices:</strong> {report_data['active_devices']}</li>
                    <li style="margin-bottom: 10px;">🔍 <strong>Scans (24h):</strong> {report_data['scans_24h']}</li>
                </ul>
            </div>
            
            {_generate_high_risk_section(report_data['high_risk_devices'])}
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; text-align: center;">
                <p style="color: #6c757d; margin-bottom: 10px;">Need help? Contact our support team.</p>
                <a href="https://yourdomain.com/support" style="color: #1976d2; text-decoration: none;">Visit Support Center</a>
            </div>
        </div>
    </body>
    </html>
    """


def _generate_high_risk_section(high_risk_devices: List[Dict[str, Any]]) -> str:
    """Generate high-risk devices section"""
    if not high_risk_devices:
        return """
        <div style="background-color: #d4edda; padding: 20px; border-radius: 6px; border-left: 4px solid #28a745;">
            <h3 style="margin-top: 0; color: #155724;">🛡️ Security Status: Good</h3>
            <p style="margin-bottom: 0; color: #155724;">No high-risk devices detected in the last 24 hours.</p>
        </div>
        """
    
    devices_html = ""
    for device in high_risk_devices:
        devices_html += f"""
        <li style="margin-bottom: 10px; padding: 10px; background-color: #fff3cd; border-radius: 4px;">
            <strong>{device['hostname']}</strong> ({device['ip_address']}) - Risk Score: {device['risk_score']}%
        </li>
        """
    
    return f"""
    <div style="background-color: #f8d7da; padding: 20px; border-radius: 6px; border-left: 4px solid #dc3545;">
        <h3 style="margin-top: 0; color: #721c24;">⚠️ High-Risk Devices</h3>
        <ul style="list-style: none; padding: 0;">
            {devices_html}
        </ul>
        <p style="margin-bottom: 0; color: #721c24;">
            <a href="https://app.yourdomain.com/devices" style="color: #721c24;">View Details →</a>
        </p>
    </div>
    """


async def _send_email(to_email: str, subject: str, html_content: str):
    """Send email using SMTP"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.FROM_EMAIL
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


@celery_app.task
def send_security_alert(tenant_id: str, alert_data: Dict[str, Any]):
    """Send immediate security alert"""
    return asyncio.run(_send_security_alert_async(tenant_id, alert_data))


async def _send_security_alert_async(tenant_id: str, alert_data: Dict[str, Any]):
    """Async implementation of security alert"""
    async with AsyncSessionLocal() as db:
        try:
            # Get tenant and users
            tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = tenant_result.scalar_one_or_none()
            
            if not tenant:
                return
            
            user_result = await db.execute(select(User).where(User.tenant_id == tenant_id))
            users = user_result.scalars().all()
            
            # Send alert to all users
            for user in users:
                await _send_email(
                    to_email=user.email,
                    subject=f"🚨 Security Alert - {alert_data.get('title', 'Critical Issue')}",
                    html_content=_generate_alert_html(tenant.name, alert_data)
                )
            
            return {'alerts_sent': len(users)}
            
        except Exception as e:
            raise Exception(f"Failed to send security alert: {str(e)}")


def _generate_alert_html(tenant_name: str, alert_data: Dict[str, Any]) -> str:
    """Generate HTML for security alert email"""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 8px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <div style="background-color: #dc3545; color: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; text-align: center;">
                <h1 style="margin: 0;">🚨 Security Alert</h1>
            </div>
            
            <h2 style="color: #333; margin-bottom: 15px;">{tenant_name}</h2>
            
            <div style="background-color: #f8d7da; padding: 20px; border-radius: 6px; border-left: 4px solid #dc3545; margin-bottom: 20px;">
                <h3 style="margin-top: 0; color: #721c24;">{alert_data.get('title', 'Security Issue Detected')}</h3>
                <p style="color: #721c24; margin-bottom: 0;">{alert_data.get('description', 'A security issue has been detected on your network.')}</p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <h4>Details:</h4>
                <ul>
                    <li><strong>Device:</strong> {alert_data.get('device', 'Unknown')}</li>
                    <li><strong>Severity:</strong> {alert_data.get('severity', 'High')}</li>
                    <li><strong>Time:</strong> {alert_data.get('timestamp', 'Now')}</li>
                </ul>
            </div>
            
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://app.yourdomain.com/devices" style="background-color: #1976d2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                    View Dashboard
                </a>
            </div>
        </div>
    </body>
    </html>
    """