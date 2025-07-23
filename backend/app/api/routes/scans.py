from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import asyncio
import nmap
import json

from ...core.database import get_db, User, Device, Scan, Port, Vulnerability
from ...core.security import get_current_user, check_subscription_limits

router = APIRouter()


# Pydantic models
class ScanCreate(BaseModel):
    device_id: int
    scan_type: str  # "quick", "full", "port", "vulnerability"


class ScanResponse(BaseModel):
    id: int
    device_id: int
    scan_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    results: Optional[Dict[str, Any]]
    error_message: Optional[str]


class ScanResults(BaseModel):
    scan_id: int
    device_ip: str
    open_ports: List[Dict[str, Any]]
    vulnerabilities: List[Dict[str, Any]]
    risk_score: float
    scan_duration: float


# Background task for scanning
def perform_scan_sync(scan_id: int, device_ip: str, scan_type: str):
    """Synchronous background task to perform the actual scan."""
    import sqlite3
    from datetime import datetime, timezone
    
    try:
        # Connect to SQLite database directly
        conn = sqlite3.connect('iot_security.db')
        cursor = conn.cursor()
        
        # Update scan status to running
        cursor.execute(
            "UPDATE scans SET status = 'running' WHERE id = ?",
            (scan_id,)
        )
        conn.commit()
        
        # Perform the scan
        scan_results = run_nmap_scan_sync(device_ip, scan_type)
        
        # Calculate risk score
        risk_score = calculate_risk_score(scan_results)
        
        # Update scan with results
        cursor.execute("""
            UPDATE scans 
            SET status = 'completed', 
                completed_at = ?, 
                results = ?
            WHERE id = ?
        """, (
            datetime.now(timezone.utc).isoformat(),
            json.dumps(scan_results),
            scan_id
        ))
        
        # Update device risk score
        cursor.execute("""
            UPDATE devices 
            SET risk_score = ?, last_seen = ?
            WHERE ip_address = ?
        """, (
            risk_score,
            datetime.now(timezone.utc).isoformat(),
            device_ip
        ))
        
        conn.commit()
        print(f"Scan {scan_id} completed successfully")
        
    except Exception as e:
        print(f"Scan {scan_id} failed: {str(e)}")
        try:
            cursor.execute("""
                UPDATE scans 
                SET status = 'failed', 
                    error_message = ?, 
                    completed_at = ?
                WHERE id = ?
            """, (
                str(e),
                datetime.now(timezone.utc).isoformat(),
                scan_id
            ))
            conn.commit()
        except:
            pass
    finally:
        if 'conn' in locals():
            conn.close()


async def run_nmap_scan(target_ip: str, scan_type: str) -> Dict[str, Any]:
    """Run nmap scan and return results."""
    nm = nmap.PortScanner()
    
    try:
        if scan_type == "quick":
            # Quick scan - top 100 ports
            nm.scan(target_ip, arguments='-T4 -F')
        elif scan_type == "full":
            # Full scan - all ports
            nm.scan(target_ip, arguments='-T4 -p-')
        elif scan_type == "port":
            # Port scan with service detection
            nm.scan(target_ip, arguments='-T4 -sV -sC')
        elif scan_type == "vulnerability":
            # Vulnerability scan
            nm.scan(target_ip, arguments='-T4 -sV -sC --script vuln')
        else:
            nm.scan(target_ip, arguments='-T4')
        
        results = {
            "scan_type": scan_type,
            "target": target_ip,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "ports": [],
            "host_info": {},
            "vulnerabilities": []
        }
        
        if target_ip in nm.all_hosts():
            host = nm[target_ip]
            
            # Host information
            results["host_info"] = {
                "state": host.state(),
                "hostname": host.hostname() if host.hostname() else None,
                "protocols": list(host.all_protocols())
            }
            
            # Port information
            for protocol in host.all_protocols():
                ports = host[protocol].keys()
                for port in ports:
                    port_info = {
                        "port": port,
                        "protocol": protocol,
                        "state": host[protocol][port]["state"],
                        "service": host[protocol][port].get("name", ""),
                        "version": host[protocol][port].get("version", ""),
                        "product": host[protocol][port].get("product", ""),
                        "banner": host[protocol][port].get("extrainfo", "")
                    }
                    results["ports"].append(port_info)
            
            # Vulnerability information (if vulnerability scan)
            if scan_type == "vulnerability" and "script" in host:
                for script_name, script_output in host["script"].items():
                    if "vuln" in script_name.lower():
                        results["vulnerabilities"].append({
                            "script": script_name,
                            "output": script_output,
                            "severity": "medium"  # Default, would need parsing
                        })
        
        return results
        
    except Exception as e:
        raise Exception(f"Scan failed: {str(e)}")


def run_nmap_scan_sync(target_ip: str, scan_type: str) -> Dict[str, Any]:
    """Synchronous version of nmap scan for background tasks."""
    from datetime import datetime, timezone
    
    nm = nmap.PortScanner()
    
    try:
        print(f"Starting {scan_type} scan on {target_ip}")
        
        if scan_type == "quick":
            # Quick scan - top 100 ports
            nm.scan(target_ip, arguments='-T4 -F')
        elif scan_type == "full":
            # Full scan - all ports  
            nm.scan(target_ip, arguments='-T4 -p-')
        elif scan_type == "port":
            # Port scan with service detection
            nm.scan(target_ip, arguments='-T4 -sV -sC')
        elif scan_type == "vulnerability":
            # Vulnerability scan
            nm.scan(target_ip, arguments='-T4 -sV -sC --script vuln')
        else:
            nm.scan(target_ip, arguments='-T4')
        
        print(f"Nmap scan completed for {target_ip}")
        
        results = {
            "scan_type": scan_type,
            "target": target_ip,
            "scan_time": datetime.now(timezone.utc).isoformat(),
            "ports": [],
            "host_info": {},
            "vulnerabilities": []
        }
        
        if target_ip in nm.all_hosts():
            host = nm[target_ip]
            
            # Host information
            results["host_info"] = {
                "state": host.state(),
                "hostname": host.hostname() if host.hostname() else None,
                "protocols": list(host.all_protocols())
            }
            
            # Port information
            for protocol in host.all_protocols():
                ports = host[protocol].keys()
                for port in ports:
                    port_info = {
                        "port": port,
                        "protocol": protocol,
                        "state": host[protocol][port]["state"],
                        "service": host[protocol][port].get("name", ""),
                        "version": host[protocol][port].get("version", ""),
                        "product": host[protocol][port].get("product", ""),
                        "banner": host[protocol][port].get("extrainfo", "")
                    }
                    results["ports"].append(port_info)
            
            # Vulnerability information (if vulnerability scan)
            if scan_type == "vulnerability" and "script" in host:
                for script_name, script_output in host["script"].items():
                    if "vuln" in script_name.lower():
                        results["vulnerabilities"].append({
                            "script": script_name,
                            "output": script_output,
                            "severity": "medium"  # Default, would need parsing
                        })
        
        print(f"Scan results processed: {len(results['ports'])} ports found")
        return results
        
    except Exception as e:
        print(f"Nmap scan failed: {str(e)}")
        raise Exception(f"Scan failed: {str(e)}")


def calculate_risk_score(scan_results: Dict[str, Any]) -> float:
    """Calculate risk score based on scan results."""
    score = 0.0
    
    # Points for open ports
    open_ports = [p for p in scan_results.get("ports", []) if p["state"] == "open"]
    score += len(open_ports) * 10
    
    # Points for common vulnerable services
    vulnerable_services = ["ftp", "telnet", "ssh", "http", "https", "smb"]
    for port in open_ports:
        if port.get("service", "").lower() in vulnerable_services:
            score += 20
    
    # Points for vulnerabilities
    vulnerabilities = scan_results.get("vulnerabilities", [])
    score += len(vulnerabilities) * 50
    
    # Normalize to 0-100 scale
    return min(100.0, score)


@router.post("/", response_model=ScanResponse)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new scan."""
    
    # Check subscription limits
    if scan_data.scan_type in ["vulnerability", "full"] and not await check_subscription_limits(current_user, "advanced_scan", db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Advanced scans not available in your subscription plan"
        )
    
    # Get device
    result = await db.execute(
        select(Device).where(
            and_(Device.id == scan_data.device_id, Device.user_id == current_user.id)
        )
    )
    device = result.scalar_one_or_none()
    
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    # Create scan record
    scan = Scan(
        user_id=current_user.id,
        device_id=device.id,
        scan_type=scan_data.scan_type,
        status="pending"
    )
    
    db.add(scan)
    await db.commit()
    await db.refresh(scan)
    
    # Start background scan using threading for sync function
    import threading
    thread = threading.Thread(
        target=perform_scan_sync,
        args=(scan.id, device.ip_address, scan_data.scan_type)
    )
    thread.daemon = True
    thread.start()
    
    return ScanResponse(
        id=scan.id,
        device_id=scan.device_id,
        scan_type=scan.scan_type,
        status=scan.status,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        results=scan.results,
        error_message=scan.error_message
    )


@router.get("/", response_model=List[ScanResponse])
async def get_scans(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """Get all scans for the current user."""
    
    result = await db.execute(
        select(Scan)
        .where(Scan.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .order_by(Scan.started_at.desc())
    )
    scans = result.scalars().all()
    
    return [
        ScanResponse(
            id=scan.id,
            device_id=scan.device_id,
            scan_type=scan.scan_type,
            status=scan.status,
            started_at=scan.started_at,
            completed_at=scan.completed_at,
            results=scan.results,
            error_message=scan.error_message
        )
        for scan in scans
    ]


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific scan."""
    
    result = await db.execute(
        select(Scan).where(
            and_(Scan.id == scan_id, Scan.user_id == current_user.id)
        )
    )
    scan = result.scalar_one_or_none()
    
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scan not found"
        )
    
    return ScanResponse(
        id=scan.id,
        device_id=scan.device_id,
        scan_type=scan.scan_type,
        status=scan.status,
        started_at=scan.started_at,
        completed_at=scan.completed_at,
        results=scan.results,
        error_message=scan.error_message
    )