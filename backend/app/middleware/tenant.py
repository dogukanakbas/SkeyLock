from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import re

from ..core.database import Tenant, get_db


class TenantMiddleware:
    """Middleware to handle multi-tenant requests"""
    
    @staticmethod
    async def get_tenant_from_request(request: Request, db: AsyncSession) -> Optional[Tenant]:
        """Extract tenant from request (subdomain or header)"""
        
        # Method 1: From subdomain (app.tenant-name.yourdomain.com)
        host = request.headers.get("host", "")
        subdomain_match = re.match(r"^([^.]+)\..*", host)
        
        if subdomain_match:
            subdomain = subdomain_match.group(1)
            if subdomain not in ["www", "api", "admin"]:  # Reserved subdomains
                result = await db.execute(
                    select(Tenant).where(Tenant.subdomain == subdomain)
                )
                tenant = result.scalar_one_or_none()
                if tenant and tenant.is_active:
                    return tenant
        
        # Method 2: From custom header (X-Tenant-ID)
        tenant_id = request.headers.get("x-tenant-id")
        if tenant_id:
            result = await db.execute(
                select(Tenant).where(Tenant.id == tenant_id)
            )
            tenant = result.scalar_one_or_none()
            if tenant and tenant.is_active:
                return tenant
        
        # Method 3: From domain mapping
        domain = request.headers.get("host", "").split(":")[0]  # Remove port
        result = await db.execute(
            select(Tenant).where(Tenant.domain == domain)
        )
        tenant = result.scalar_one_or_none()
        if tenant and tenant.is_active:
            return tenant
        
        return None
    
    @staticmethod
    async def get_or_create_default_tenant(db: AsyncSession) -> Tenant:
        """Get or create default tenant for development"""
        result = await db.execute(
            select(Tenant).where(Tenant.subdomain == "default")
        )
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            tenant = Tenant(
                name="Default Tenant",
                domain="localhost",
                subdomain="default",
                plan_type="professional",  # Give full access for development
                max_devices=1000,
                max_users=100,
                max_scans_per_month=10000
            )
            db.add(tenant)
            await db.commit()
            await db.refresh(tenant)
        
        return tenant


async def get_current_tenant(request: Request, db: AsyncSession) -> Tenant:
    """Dependency to get current tenant"""
    tenant = await TenantMiddleware.get_tenant_from_request(request, db)
    
    if not tenant:
        # For development, create/use default tenant
        tenant = await TenantMiddleware.get_or_create_default_tenant(db)
    
    if not tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant account is suspended"
        )
    
    return tenant