from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import AsyncGenerator
import uuid

from .config import settings

# Database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


# Tenant Model
class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    subdomain = Column(String, unique=True, nullable=False)
    
    # Subscription info
    plan_type = Column(String, default="trial")
    status = Column(String, default="active")
    
    # Limits
    max_devices = Column(Integer, default=5)
    max_users = Column(Integer, default=1)
    max_scans_per_month = Column(Integer, default=100)
    
    # Billing
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    billing_email = Column(String)
    
    # Settings
    settings = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    
    # Relationships
    users = relationship("User", back_populates="tenant")
    devices = relationship("Device", back_populates="tenant")
    scans = relationship("Scan", back_populates="tenant")


# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, index=True, nullable=False)  # Removed unique=True for multi-tenant
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    company_name = Column(String)
    phone = Column(String)
    job_title = Column(String)
    company_size = Column(String)  # "1-10", "11-50", "51-200", "201-1000", "1000+"
    industry = Column(String)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    role = Column(String, default="user")  # user, admin, owner
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    subscription = relationship("Subscription", back_populates="user", uselist=False)
    devices = relationship("Device", back_populates="user")
    scans = relationship("Scan", back_populates="user")


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    plan_type = Column(String)  # demo, starter, professional, enterprise
    status = Column(String)  # active, canceled, expired, trial
    stripe_customer_id = Column(String)
    stripe_subscription_id = Column(String)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    trial_end = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="subscription")


class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    ip_address = Column(String, nullable=False)
    mac_address = Column(String)
    hostname = Column(String)
    device_type = Column(String)
    manufacturer = Column(String)
    model = Column(String)
    firmware_version = Column(String)
    first_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_seen = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = Column(Boolean, default=True)
    risk_score = Column(Float, default=0.0)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="devices")
    user = relationship("User", back_populates="devices")
    scans = relationship("Scan", back_populates="device")
    vulnerabilities = relationship("Vulnerability", back_populates="device")
    ports = relationship("Port", back_populates="device")


class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))
    scan_type = Column(String)  # full, quick, port, vulnerability
    status = Column(String)  # pending, running, completed, failed
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    results = Column(JSON)
    error_message = Column(Text)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="scans")
    user = relationship("User", back_populates="scans")
    device = relationship("Device", back_populates="scans")


class Vulnerability(Base):
    __tablename__ = "vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    cve_id = Column(String)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(String)  # low, medium, high, critical
    cvss_score = Column(Float)
    status = Column(String, default="open")  # open, fixed, ignored
    first_detected = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_detected = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    device = relationship("Device", back_populates="vulnerabilities")


class Port(Base):
    __tablename__ = "ports"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    port_number = Column(Integer, nullable=False)
    protocol = Column(String, nullable=False)  # tcp, udp
    service = Column(String)
    version = Column(String)
    state = Column(String)  # open, closed, filtered
    banner = Column(Text)
    last_scanned = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    device = relationship("Device", back_populates="ports")


# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()