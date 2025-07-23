from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel, IPvAnyAddress
from typing import List, Optional
from datetime import datetime, timezone

from ...core.database import get_db, User, Device, Port, Vulnerability
from ...core.security import get_current_user, check_subscription_limits

router = APIRouter()


# Pydantic models
class DeviceCreate(BaseModel):
    ip_address: str
    mac_address: Optional[str] = None
    hostname: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None


class DeviceResponse(BaseModel):
    id: int
    ip_address: str
    mac_address: Optional[str]
    hostname: Optional[str]
    device_type: Optional[str]
    manufacturer: Optional[str]
    model: Optional[str]
    firmware_version: Optional[str]
    first_seen: datetime
    last_seen: datetime
    is_active: bool
    risk_score: float
    open_ports_count: int
    vulnerabilities_count: int
    critical_vulnerabilities: int


class DeviceUpdate(BaseModel):
    hostname: Optional[str] = None
    device_type: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    firmware_version: Optional[str] = None


@router.get("/", response_model=List[DeviceResponse])
async def get_devices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Get all devices for the current user."""
    
    result = await db.execute(
        select(Device)
        .where(Device.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Device.last_seen.desc())
    )
    devices = result.scalars().all()
    
    device_responses = []
    for device in devices:
        # Count open ports
        ports_result = await db.execute(
            select(Port).where(
                and_(Port.device_id == device.id, Port.state == "open")
            )
        )
        open_ports_count = len(ports_result.scalars().all())
        
        # Count vulnerabilities
        vulns_result = await db.execute(
            select(Vulnerability).where(Vulnerability.device_id == device.id)
        )
        vulnerabilities = vulns_result.scalars().all()
        vulnerabilities_count = len(vulnerabilities)
        critical_vulnerabilities = len([v for v in vulnerabilities if v.severity == "critical"])
        
        device_responses.append(DeviceResponse(
            id=device.id,
            ip_address=device.ip_address,
            mac_address=device.mac_address,
            hostname=device.hostname,
            device_type=device.device_type,
            manufacturer=device.manufacturer,
            model=device.model,
            firmware_version=device.firmware_version,
            first_seen=device.first_seen,
            last_seen=device.last_seen,
            is_active=device.is_active,
            risk_score=device.risk_score,
            open_ports_count=open_ports_count,
            vulnerabilities_count=vulnerabilities_count,
            critical_vulnerabilities=critical_vulnerabilities
        ))
    
    return device_responses


@router.post("/", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a new device."""
    
    # Check subscription limits
    if not await check_subscription_limits(current_user, "scan_device", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device limit reached for your subscription plan"
        )
    
    # Check if device already exists
    result = await db.execute(
        select(Device).where(
            and_(
                Device.user_id == current_user.id,
                Device.ip_address == device_data.ip_address
            )
        )
    )
    existing_device = result.scalar_one_or_none()
    
    if existing_device:
        # Update last_seen and reactivate if needed
        existing_device.last_seen = datetime.now(timezone.utc)
        existing_device.is_active = True
        if device_data.hostname:
            existing_device.hostname = device_data.hostname
        if device_data.device_type:
            existing_device.device_type = device_data.device_type
        if device_data.manufacturer:
            existing_device.manufacturer = device_data.manufacturer
        if device_data.model:
            existing_device.model = device_data.model
        if device_data.firmware_version:
            existing_device.firmware_version = device_data.firmware_version
        
        await db.commit()
        return DeviceResponse(
            id=existing_device.id,
            ip_address=existing_device.ip_address,
            mac_address=existing_device.mac_address,
            hostname=existing_device.hostname,
            device_type=existing_device.device_type,
            manufacturer=existing_device.manufacturer,
            model=existing_device.model,
            firmware_version=existing_device.firmware_version,
            first_seen=existing_device.first_seen,
            last_seen=existing_device.last_seen,
            is_active=existing_device.is_active,
            risk_score=existing_device.risk_score,
            open_ports_count=0,
            vulnerabilities_count=0,
            critical_vulnerabilities=0
        )
    
    # Create new device
    device = Device(
        user_id=current_user.id,
        ip_address=device_data.ip_address,
        mac_address=device_data.mac_address,
        hostname=device_data.hostname,
        device_type=device_data.device_type,
        manufacturer=device_data.manufacturer,
        model=device_data.model,
        firmware_version=device_data.firmware_version
    )
    
    db.add(device)
    await db.commit()
    await db.refresh(device)
    
    return DeviceResponse(
        id=device.id,
        ip_address=device.ip_address,
        mac_address=device.mac_address,
        hostname=device.hostname,
        device_type=device.device_type,
        manufacturer=device.manufacturer,
        model=device.model,
        firmware_version=device.firmware_version,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        is_active=device.is_active,
        risk_score=device.risk_score,
        open_ports_count=0,
        vulnerabilities_count=0,
        critical_vulnerabilities=0
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific device."""
    
    result = await db.execute(
        select(Device).where(
            and_(Device.id == device_id, Device.user_id == current_user.id)
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Get additional info
    ports_result = await db.execute(
        select(Port).where(and_(Port.device_id == device.id, Port.state == "open"))
    )
    open_ports_count = len(ports_result.scalars().all())
    
    vulns_result = await db.execute(
        select(Vulnerability).where(Vulnerability.device_id == device.id)
    )
    vulnerabilities = vulns_result.scalars().all()
    vulnerabilities_count = len(vulnerabilities)
    critical_vulnerabilities = len([v for v in vulnerabilities if v.severity == "critical"])
    
    return DeviceResponse(
        id=device.id,
        ip_address=device.ip_address,
        mac_address=device.mac_address,
        hostname=device.hostname,
        device_type=device.device_type,
        manufacturer=device.manufacturer,
        model=device.model,
        firmware_version=device.firmware_version,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        is_active=device.is_active,
        risk_score=device.risk_score,
        open_ports_count=open_ports_count,
        vulnerabilities_count=vulnerabilities_count,
        critical_vulnerabilities=critical_vulnerabilities
    )


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: int,
    device_data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a device."""
    
    result = await db.execute(
        select(Device).where(
            and_(Device.id == device_id, Device.user_id == current_user.id)
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Update fields
    if device_data.hostname is not None:
        device.hostname = device_data.hostname
    if device_data.device_type is not None:
        device.device_type = device_data.device_type
    if device_data.manufacturer is not None:
        device.manufacturer = device_data.manufacturer
    if device_data.model is not None:
        device.model = device_data.model
    if device_data.firmware_version is not None:
        device.firmware_version = device_data.firmware_version
    
    device.updated_at = datetime.now(timezone.utc)
    
    await db.commit()
    
    return DeviceResponse(
        id=device.id,
        ip_address=device.ip_address,
        mac_address=device.mac_address,
        hostname=device.hostname,
        device_type=device.device_type,
        manufacturer=device.manufacturer,
        model=device.model,
        firmware_version=device.firmware_version,
        first_seen=device.first_seen,
        last_seen=device.last_seen,
        is_active=device.is_active,
        risk_score=device.risk_score,
        open_ports_count=0,
        vulnerabilities_count=0,
        critical_vulnerabilities=0
    )


@router.delete("/{device_id}")
async def delete_device(
    device_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a device."""
    
    result = await db.execute(
        select(Device).where(
            and_(Device.id == device_id, Device.user_id == current_user.id)
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    await db.delete(device)
    await db.commit()
    
    return {"message": "Device deleted successfully"}