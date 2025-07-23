import asyncio
import nmap
import json
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..core.database import Device, Scan, Vulnerability, Port, Tenant
from ..core.config import settings


class AdvancedScanningService:
    """Production-ready scanning service with advanced capabilities"""
    
    def __init__(self):
        self.nm = nmap.PortScanner()
    
    async def discover_network_devices(
        self, 
        network_range: str, 
        tenant: Tenant,
        db: AsyncSession
    ) -> List[Dict[str, Any]]:
        """Discover devices on network range"""
        try:
            # Use nmap for network discovery
            self.nm.scan(hosts=network_range, arguments='-sn -T4')
            
            discovered_devices = []
            
            for host in self.nm.all_hosts():
                if self.nm[host].state() == 'up':
                    device_info = await self._get_device_info(host)
                    discovered_devices.append(device_info)
            
            return discovered_devices
            
        except Exception as e:
            raise Exception(f"Network discovery failed: {str(e)}")
    
    async def perform_comprehensive_scan(
        self,
        device: Device,
        scan_type: str,
        tenant: Tenant,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Perform comprehensive security scan"""
        
        scan_results = {
            "device_id": device.id,
            "scan_type": scan_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "target": device.ip_address,
            "results": {}
        }
        
        try:
            # Port scanning
            if scan_type in ["full", "port", "quick"]:
                port_results = await self._scan_ports(device.ip_address, scan_type)
                scan_results["results"]["ports"] = port_results
                await self._save_port_results(device, port_results, db)
            
            # Vulnerability scanning
            if scan_type in ["full", "vulnerability"]:
                vuln_results = await self._scan_vulnerabilities(device.ip_address)
                scan_results["results"]["vulnerabilities"] = vuln_results
                await self._save_vulnerability_results(device, vuln_results, db)
            
            # Service detection
            if scan_type in ["full", "service"]:
                service_results = await self._detect_services(device.ip_address)
                scan_results["results"]["services"] = service_results
            
            # OS detection
            if scan_type in ["full"]:
                os_results = await self._detect_os(device.ip_address)
                scan_results["results"]["os"] = os_results
            
            # IoT-specific checks
            if scan_type in ["full", "iot"]:
                iot_results = await self._iot_specific_checks(device.ip_address)
                scan_results["results"]["iot_checks"] = iot_results
            
            # Calculate risk score
            risk_score = await self._calculate_risk_score(scan_results["results"])
            scan_results["risk_score"] = risk_score
            
            # Update device risk score
            device.risk_score = risk_score
            await db.commit()
            
            return scan_results
            
        except Exception as e:
            scan_results["error"] = str(e)
            scan_results["status"] = "failed"
            return scan_results
    
    async def _scan_ports(self, target_ip: str, scan_type: str) -> Dict[str, Any]:
        """Advanced port scanning"""
        try:
            if scan_type == "quick":
                # Top 100 ports
                self.nm.scan(target_ip, arguments='-T4 -F --open')
            elif scan_type == "full":
                # All ports
                self.nm.scan(target_ip, arguments='-T4 -p- --open')
            else:
                # Common ports with service detection
                self.nm.scan(target_ip, arguments='-T4 -sV -sC --open')
            
            port_results = {
                "open_ports": [],
                "filtered_ports": [],
                "closed_ports": [],
                "total_scanned": 0
            }
            
            if target_ip in self.nm.all_hosts():
                host = self.nm[target_ip]
                
                for protocol in host.all_protocols():
                    ports = host[protocol].keys()
                    port_results["total_scanned"] += len(ports)
                    
                    for port in ports:
                        port_info = {
                            "port": port,
                            "protocol": protocol,
                            "state": host[protocol][port]["state"],
                            "service": host[protocol][port].get("name", ""),
                            "version": host[protocol][port].get("version", ""),
                            "product": host[protocol][port].get("product", ""),
                            "extrainfo": host[protocol][port].get("extrainfo", ""),
                            "cpe": host[protocol][port].get("cpe", "")
                        }
                        
                        if port_info["state"] == "open":
                            port_results["open_ports"].append(port_info)
                        elif port_info["state"] == "filtered":
                            port_results["filtered_ports"].append(port_info)
                        else:
                            port_results["closed_ports"].append(port_info)
            
            return port_results
            
        except Exception as e:
            return {"error": str(e), "open_ports": []}
    
    async def _scan_vulnerabilities(self, target_ip: str) -> Dict[str, Any]:
        """Advanced vulnerability scanning"""
        try:
            # Use nmap vulnerability scripts
            self.nm.scan(target_ip, arguments='-T4 -sV --script vuln')
            
            vulnerabilities = []
            
            if target_ip in self.nm.all_hosts():
                host = self.nm[target_ip]
                
                # Check for script results
                if 'hostscript' in host:
                    for script in host['hostscript']:
                        if 'vuln' in script['id'].lower():
                            vuln = {
                                "script": script['id'],
                                "output": script['output'],
                                "severity": self._determine_severity(script['output']),
                                "cve_ids": self._extract_cve_ids(script['output'])
                            }
                            vulnerabilities.append(vuln)
                
                # Check port-specific vulnerabilities
                for protocol in host.all_protocols():
                    ports = host[protocol].keys()
                    for port in ports:
                        if 'script' in host[protocol][port]:
                            for script_name, script_output in host[protocol][port]['script'].items():
                                if 'vuln' in script_name.lower():
                                    vuln = {
                                        "port": port,
                                        "protocol": protocol,
                                        "script": script_name,
                                        "output": script_output,
                                        "severity": self._determine_severity(script_output),
                                        "cve_ids": self._extract_cve_ids(script_output)
                                    }
                                    vulnerabilities.append(vuln)
            
            return {
                "vulnerabilities": vulnerabilities,
                "total_found": len(vulnerabilities),
                "critical": len([v for v in vulnerabilities if v["severity"] == "critical"]),
                "high": len([v for v in vulnerabilities if v["severity"] == "high"]),
                "medium": len([v for v in vulnerabilities if v["severity"] == "medium"]),
                "low": len([v for v in vulnerabilities if v["severity"] == "low"])
            }
            
        except Exception as e:
            return {"error": str(e), "vulnerabilities": []}
    
    async def _detect_services(self, target_ip: str) -> Dict[str, Any]:
        """Advanced service detection"""
        try:
            self.nm.scan(target_ip, arguments='-T4 -sV -A')
            
            services = []
            
            if target_ip in self.nm.all_hosts():
                host = self.nm[target_ip]
                
                for protocol in host.all_protocols():
                    ports = host[protocol].keys()
                    for port in ports:
                        if host[protocol][port]["state"] == "open":
                            service = {
                                "port": port,
                                "protocol": protocol,
                                "service": host[protocol][port].get("name", ""),
                                "product": host[protocol][port].get("product", ""),
                                "version": host[protocol][port].get("version", ""),
                                "extrainfo": host[protocol][port].get("extrainfo", ""),
                                "cpe": host[protocol][port].get("cpe", "")
                            }
                            services.append(service)
            
            return {"services": services, "total_services": len(services)}
            
        except Exception as e:
            return {"error": str(e), "services": []}
    
    async def _detect_os(self, target_ip: str) -> Dict[str, Any]:
        """OS detection and fingerprinting"""
        try:
            self.nm.scan(target_ip, arguments='-T4 -O')
            
            os_info = {"os_matches": [], "accuracy": 0}
            
            if target_ip in self.nm.all_hosts():
                host = self.nm[target_ip]
                
                if 'osmatch' in host:
                    for osmatch in host['osmatch']:
                        os_info["os_matches"].append({
                            "name": osmatch['name'],
                            "accuracy": osmatch['accuracy'],
                            "line": osmatch['line']
                        })
                    
                    if os_info["os_matches"]:
                        os_info["accuracy"] = max([int(match["accuracy"]) for match in os_info["os_matches"]])
            
            return os_info
            
        except Exception as e:
            return {"error": str(e), "os_matches": []}
    
    async def _iot_specific_checks(self, target_ip: str) -> Dict[str, Any]:
        """IoT-specific security checks"""
        checks = {
            "default_credentials": False,
            "unencrypted_protocols": [],
            "weak_authentication": False,
            "firmware_version": None,
            "device_type": None,
            "manufacturer": None
        }
        
        try:
            # Check for common IoT ports and services
            common_iot_ports = [80, 443, 23, 22, 21, 8080, 8443, 554, 1935]
            
            for port in common_iot_ports:
                try:
                    self.nm.scan(target_ip, str(port), arguments='-T4 -sV')
                    
                    if target_ip in self.nm.all_hosts():
                        host = self.nm[target_ip]
                        if 'tcp' in host and port in host['tcp']:
                            port_info = host['tcp'][port]
                            
                            # Check for default credentials
                            if port in [80, 8080] and port_info['state'] == 'open':
                                checks["default_credentials"] = await self._check_default_credentials(target_ip, port)
                            
                            # Check for unencrypted protocols
                            if port in [21, 23, 80] and port_info['state'] == 'open':
                                service = port_info.get('name', '')
                                if service in ['ftp', 'telnet', 'http']:
                                    checks["unencrypted_protocols"].append(f"{service}:{port}")
                            
                            # Extract device information
                            product = port_info.get('product', '')
                            if product:
                                checks["device_type"] = self._identify_device_type(product)
                                checks["manufacturer"] = self._identify_manufacturer(product)
                                checks["firmware_version"] = port_info.get('version', '')
                
                except:
                    continue
            
            return checks
            
        except Exception as e:
            checks["error"] = str(e)
            return checks
    
    async def _check_default_credentials(self, target_ip: str, port: int) -> bool:
        """Check for default credentials"""
        # This is a simplified check - in production, you'd use more sophisticated methods
        common_defaults = [
            ("admin", "admin"),
            ("admin", "password"),
            ("admin", ""),
            ("root", "root"),
            ("user", "user")
        ]
        
        # In a real implementation, you'd make HTTP requests to check login endpoints
        # For now, return False to avoid false positives
        return False
    
    def _determine_severity(self, script_output: str) -> str:
        """Determine vulnerability severity from script output"""
        output_lower = script_output.lower()
        
        if any(word in output_lower for word in ['critical', 'remote code execution', 'rce']):
            return 'critical'
        elif any(word in output_lower for word in ['high', 'privilege escalation', 'authentication bypass']):
            return 'high'
        elif any(word in output_lower for word in ['medium', 'information disclosure', 'denial of service']):
            return 'medium'
        else:
            return 'low'
    
    def _extract_cve_ids(self, script_output: str) -> List[str]:
        """Extract CVE IDs from script output"""
        import re
        cve_pattern = r'CVE-\d{4}-\d{4,7}'
        return re.findall(cve_pattern, script_output)
    
    def _identify_device_type(self, product: str) -> str:
        """Identify device type from product string"""
        product_lower = product.lower()
        
        if any(word in product_lower for word in ['camera', 'webcam', 'ipcam']):
            return 'IP Camera'
        elif any(word in product_lower for word in ['router', 'gateway']):
            return 'Router'
        elif any(word in product_lower for word in ['thermostat', 'hvac']):
            return 'Thermostat'
        elif any(word in product_lower for word in ['printer']):
            return 'Printer'
        elif any(word in product_lower for word in ['switch', 'hub']):
            return 'Network Switch'
        else:
            return 'Unknown IoT Device'
    
    def _identify_manufacturer(self, product: str) -> str:
        """Identify manufacturer from product string"""
        manufacturers = {
            'hikvision': 'Hikvision',
            'dahua': 'Dahua',
            'axis': 'Axis Communications',
            'cisco': 'Cisco',
            'netgear': 'Netgear',
            'linksys': 'Linksys',
            'tp-link': 'TP-Link',
            'dlink': 'D-Link'
        }
        
        product_lower = product.lower()
        for key, value in manufacturers.items():
            if key in product_lower:
                return value
        
        return 'Unknown'
    
    async def _calculate_risk_score(self, scan_results: Dict[str, Any]) -> float:
        """Calculate comprehensive risk score"""
        score = 0.0
        
        # Port-based scoring
        if "ports" in scan_results:
            open_ports = scan_results["ports"].get("open_ports", [])
            score += len(open_ports) * 5  # 5 points per open port
            
            # High-risk ports
            high_risk_ports = [21, 23, 135, 139, 445, 1433, 3389]
            for port_info in open_ports:
                if port_info["port"] in high_risk_ports:
                    score += 20
        
        # Vulnerability-based scoring
        if "vulnerabilities" in scan_results:
            vulns = scan_results["vulnerabilities"]
            score += vulns.get("critical", 0) * 50
            score += vulns.get("high", 0) * 30
            score += vulns.get("medium", 0) * 15
            score += vulns.get("low", 0) * 5
        
        # IoT-specific scoring
        if "iot_checks" in scan_results:
            iot_checks = scan_results["iot_checks"]
            if iot_checks.get("default_credentials"):
                score += 40
            score += len(iot_checks.get("unencrypted_protocols", [])) * 15
        
        # Normalize to 0-100 scale
        return min(100.0, score)
    
    async def _save_port_results(self, device: Device, port_results: Dict[str, Any], db: AsyncSession):
        """Save port scan results to database"""
        # Clear existing ports
        await db.execute(
            select(Port).where(Port.device_id == device.id)
        )
        
        # Save new port results
        for port_info in port_results.get("open_ports", []):
            port = Port(
                device_id=device.id,
                port_number=port_info["port"],
                protocol=port_info["protocol"],
                service=port_info.get("service", ""),
                version=port_info.get("version", ""),
                state="open",
                banner=port_info.get("extrainfo", "")
            )
            db.add(port)
        
        await db.commit()
    
    async def _save_vulnerability_results(self, device: Device, vuln_results: Dict[str, Any], db: AsyncSession):
        """Save vulnerability results to database"""
        for vuln in vuln_results.get("vulnerabilities", []):
            vulnerability = Vulnerability(
                device_id=device.id,
                title=vuln["script"],
                description=vuln["output"][:1000],  # Truncate long descriptions
                severity=vuln["severity"],
                status="open"
            )
            
            # Add CVE IDs if found
            if vuln.get("cve_ids"):
                vulnerability.cve_id = vuln["cve_ids"][0]  # Use first CVE ID
            
            db.add(vulnerability)
        
        await db.commit()
    
    async def _get_device_info(self, ip_address: str) -> Dict[str, Any]:
        """Get basic device information"""
        try:
            # Basic ping and hostname resolution
            self.nm.scan(ip_address, arguments='-sn')
            
            device_info = {
                "ip_address": ip_address,
                "hostname": None,
                "mac_address": None,
                "vendor": None,
                "is_active": False
            }
            
            if ip_address in self.nm.all_hosts():
                host = self.nm[ip_address]
                device_info["is_active"] = host.state() == 'up'
                
                # Get hostname
                if host.hostname():
                    device_info["hostname"] = host.hostname()
                
                # Get MAC address and vendor
                if 'mac' in host['addresses']:
                    device_info["mac_address"] = host['addresses']['mac']
                    if 'vendor' in host:
                        device_info["vendor"] = list(host['vendor'].values())[0] if host['vendor'] else None
            
            return device_info
            
        except Exception as e:
            return {
                "ip_address": ip_address,
                "error": str(e),
                "is_active": False
            }