from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from ..core.database import Base


class Tenant(Base):
    __tablename__ = "tenants"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, nullable=False)
    subdomain = Column(String, unique=True, nullable=False)
    
    # Subscription info
    plan_type = Column(String, default="trial")  # trial, starter, professional, enterprise
    status = Column(String, default="active")    # active, suspended, cancelled
    
    # Limits based on plan
    max_devices = Column(Integer, default=5)     # Device limit
    max_users = Column(Integer, default=1)       # User limit
    max_scans_per_month = Column(Integer, default=100)
    
    # Billing info
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
    
    def __repr__(self):
        return f"<Tenant {self.name} ({self.domain})>"
    
    @property
    def is_trial(self):
        return self.plan_type == "trial"
    
    @property
    def is_premium(self):
        return self.plan_type in ["professional", "enterprise"]
    
    def can_add_device(self, current_device_count):
        return current_device_count < self.max_devices
    
    def can_add_user(self, current_user_count):
        return current_user_count < self.max_users
    
    def can_perform_scan(self, scans_this_month):
        return scans_this_month < self.max_scans_per_month