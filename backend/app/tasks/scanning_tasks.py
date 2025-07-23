from celery import current_task
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import asyncio
from typing import Dict, Any

from ..celery_app import celery_app
from ..core.database import AsyncSessionLocal, Tenant, Device, Scan
from ..services.scanning_service import AdvancedScanningService


@celery_app.task(bind=True)
def perform_device_scan(self, device_id: int, scan_type: str, tenant_id: str):
    """Background task to perform device scanning"""
    return asyncio.run(_perform_device_scan_async(self, device_id, scan_type, tenant_id))


async def _perform_device_scan_async(task, device_id: int, scan_type: str, tenant_id: str):
    """Async implementation of device scanning"""
    async with AsyncSessionLocal() as db:
        try:
            # Update task status
            task.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting scan...'})
            
            # Get device and tenant
            device_result = await db.execute(select(Device).where(Device.id == device_id))
            device = device_result.scalar_one_or_none()
            
            tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = tenant_result.scalar_one_or_none()
            
            if not device or not tenant:
                raise Exception("Device or tenant not found")
            
            # Create scan record
            scan = Scan(
                tenant_id=tenant_id,
                user_id=device.user_id,
                device_id=device_id,
                scan_type=scan_type,
                status="running"
            )
            db.add(scan)
            await db.commit()
            await db.refresh(scan)
            
            task.update_state(state='PROGRESS', meta={'progress': 10, 'status': 'Scan created...'})
            
            # Perform scanning
            scanning_service = AdvancedScanningService()
            
            task.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Starting port scan...'})
            
            scan_results = await scanning_service.perform_comprehensive_scan(
                device, scan_type, tenant, db
            )
            
            task.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Processing results...'})
            
            # Update scan with results
            scan.status = "completed"
            scan.completed_at = scan_results.get("timestamp")
            scan.results = scan_results
            
            await db.commit()
            
            task.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Scan completed'})
            
            return {
                'scan_id': scan.id,
                'device_id': device_id,
                'status': 'completed',
                'results': scan_results
            }
            
        except Exception as e:
            # Update scan status to failed
            if 'scan' in locals():
                scan.status = "failed"
                scan.error_message = str(e)
                await db.commit()
            
            raise Exception(f"Scan failed: {str(e)}")


@celery_app.task(bind=True)
def discover_network_devices(self, network_range: str, tenant_id: str):
    """Background task for network device discovery"""
    return asyncio.run(_discover_network_devices_async(self, network_range, tenant_id))


async def _discover_network_devices_async(task, network_range: str, tenant_id: str):
    """Async implementation of network discovery"""
    async with AsyncSessionLocal() as db:
        try:
            task.update_state(state='PROGRESS', meta={'progress': 0, 'status': 'Starting discovery...'})
            
            # Get tenant
            tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
            tenant = tenant_result.scalar_one_or_none()
            
            if not tenant:
                raise Exception("Tenant not found")
            
            # Perform network discovery
            scanning_service = AdvancedScanningService()
            
            task.update_state(state='PROGRESS', meta={'progress': 20, 'status': 'Scanning network...'})
            
            discovered_devices = await scanning_service.discover_network_devices(
                network_range, tenant, db
            )
            
            task.update_state(state='PROGRESS', meta={'progress': 80, 'status': 'Processing devices...'})
            
            # Add new devices to database
            new_devices = []
            for device_info in discovered_devices:
                if device_info.get("is_active"):
                    # Check if device already exists
                    existing_device = await db.execute(
                        select(Device).where(
                            Device.tenant_id == tenant_id,
                            Device.ip_address == device_info["ip_address"]
                        )
                    )
                    
                    if not existing_device.scalar_one_or_none():
                        # Create new device
                        device = Device(
                            tenant_id=tenant_id,
                            ip_address=device_info["ip_address"],
                            hostname=device_info.get("hostname"),
                            mac_address=device_info.get("mac_address"),
                            manufacturer=device_info.get("vendor"),
                            is_active=True
                        )
                        db.add(device)
                        new_devices.append(device_info)
            
            await db.commit()
            
            task.update_state(state='PROGRESS', meta={'progress': 100, 'status': 'Discovery completed'})
            
            return {
                'network_range': network_range,
                'total_discovered': len(discovered_devices),
                'new_devices': len(new_devices),
                'devices': new_devices
            }
            
        except Exception as e:
            raise Exception(f"Network discovery failed: {str(e)}")


@celery_app.task
def schedule_periodic_scans():
    """Schedule periodic scans for all active devices"""
    return asyncio.run(_schedule_periodic_scans_async())


async def _schedule_periodic_scans_async():
    """Async implementation of periodic scan scheduling"""
    async with AsyncSessionLocal() as db:
        try:
            # Get all active devices
            result = await db.execute(
                select(Device).where(Device.is_active == True)
            )
            devices = result.scalars().all()
            
            scheduled_scans = 0
            
            for device in devices:
                # Schedule a quick scan for each device
                perform_device_scan.delay(
                    device_id=device.id,
                    scan_type="quick",
                    tenant_id=device.tenant_id
                )
                scheduled_scans += 1
            
            return {
                'total_devices': len(devices),
                'scheduled_scans': scheduled_scans
            }
            
        except Exception as e:
            raise Exception(f"Failed to schedule periodic scans: {str(e)}")


@celery_app.task
def cleanup_old_scans():
    """Cleanup old scan results to save storage"""
    return asyncio.run(_cleanup_old_scans_async())


async def _cleanup_old_scans_async():
    """Async implementation of scan cleanup"""
    async with AsyncSessionLocal() as db:
        try:
            from datetime import datetime, timedelta
            
            # Delete scans older than 90 days
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            
            result = await db.execute(
                select(Scan).where(Scan.started_at < cutoff_date)
            )
            old_scans = result.scalars().all()
            
            for scan in old_scans:
                await db.delete(scan)
            
            await db.commit()
            
            return {
                'deleted_scans': len(old_scans),
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Failed to cleanup old scans: {str(e)}")