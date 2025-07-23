from fastapi import Request, Response, HTTPException, status
from fastapi.security import HTTPBearer
import re
import html
from typing import Dict, Any
import json


class SecurityMiddleware:
    """Production-ready security middleware"""
    
    @staticmethod
    async def add_security_headers(request: Request, call_next):
        """Add security headers to all responses"""
        response = await call_next(request)
        
        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' https:; connect-src 'self' https:; frame-ancestors 'none';",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Cross-Origin-Embedder-Policy": "require-corp",
            "Cross-Origin-Opener-Policy": "same-origin",
            "Cross-Origin-Resource-Policy": "same-origin"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
        
        # Remove server header
        if "server" in response.headers:
            del response.headers["server"]
        
        return response
    
    @staticmethod
    async def validate_input(request: Request, call_next):
        """Validate and sanitize input data"""
        
        # Skip validation for GET requests and health checks
        if request.method == "GET" or request.url.path in ["/health", "/metrics"]:
            return await call_next(request)
        
        try:
            # Check content type
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                # Read and validate JSON body
                body = await request.body()
                if body:
                    try:
                        json_data = json.loads(body)
                        
                        # Validate JSON structure
                        if not isinstance(json_data, (dict, list)):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Invalid JSON structure"
                            )
                        
                        # Check for potential XSS/injection attempts
                        if SecurityMiddleware._contains_malicious_content(json_data):
                            raise HTTPException(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                detail="Potentially malicious content detected"
                            )
                        
                    except json.JSONDecodeError:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid JSON format"
                        )
            
            # Validate query parameters
            for param, value in request.query_params.items():
                if SecurityMiddleware._contains_malicious_content(value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Potentially malicious content in parameter: {param}"
                    )
            
            # Validate headers
            suspicious_headers = ["x-forwarded-for", "x-real-ip", "x-originating-ip"]
            for header in suspicious_headers:
                value = request.headers.get(header)
                if value and not SecurityMiddleware._is_valid_ip(value):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid {header} header"
                    )
            
            return await call_next(request)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Input validation error"
            )
    
    @staticmethod
    def _contains_malicious_content(data: Any) -> bool:
        """Check for potentially malicious content"""
        
        # Convert data to string for analysis
        if isinstance(data, dict):
            content = json.dumps(data)
        elif isinstance(data, list):
            content = json.dumps(data)
        else:
            content = str(data)
        
        content_lower = content.lower()
        
        # SQL injection patterns
        sql_patterns = [
            r"(\b(select|insert|update|delete|drop|create|alter|exec|execute)\b)",
            r"(\bunion\b.*\bselect\b)",
            r"(\bor\b.*=.*)",
            r"(\band\b.*=.*)",
            r"(--|#|/\*|\*/)",
            r"(\bxp_cmdshell\b)",
            r"(\bsp_executesql\b)"
        ]
        
        # XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
            r"<object[^>]*>",
            r"<embed[^>]*>",
            r"<link[^>]*>",
            r"<meta[^>]*>"
        ]
        
        # Command injection patterns
        command_patterns = [
            r"(\||&|;|\$\(|\`)",
            r"(wget|curl|nc|netcat)",
            r"(/bin/|/usr/bin/|cmd\.exe)",
            r"(rm\s+-rf|del\s+/)",
        ]
        
        # LDAP injection patterns
        ldap_patterns = [
            r"(\*\)|\(\|)",
            r"(\)\(|\&\()",
        ]
        
        all_patterns = sql_patterns + xss_patterns + command_patterns + ldap_patterns
        
        for pattern in all_patterns:
            if re.search(pattern, content_lower, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def _is_valid_ip(ip_string: str) -> bool:
        """Validate IP address format"""
        # IPv4 pattern
        ipv4_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        
        # IPv6 pattern (simplified)
        ipv6_pattern = r"^(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$"
        
        return bool(re.match(ipv4_pattern, ip_string) or re.match(ipv6_pattern, ip_string))
    
    @staticmethod
    async def log_security_events(request: Request, call_next):
        """Log security-related events"""
        import logging
        
        # Set up security logger
        security_logger = logging.getLogger("security")
        
        try:
            response = await call_next(request)
            
            # Log suspicious activities
            if response.status_code == 401:
                security_logger.warning(
                    f"Unauthorized access attempt from {request.client.host} to {request.url.path}"
                )
            elif response.status_code == 403:
                security_logger.warning(
                    f"Forbidden access attempt from {request.client.host} to {request.url.path}"
                )
            elif response.status_code == 429:
                security_logger.warning(
                    f"Rate limit exceeded from {request.client.host} to {request.url.path}"
                )
            
            return response
            
        except HTTPException as e:
            if e.status_code in [400, 401, 403, 429]:
                security_logger.warning(
                    f"Security event: {e.status_code} from {request.client.host} to {request.url.path} - {e.detail}"
                )
            raise
        except Exception as e:
            security_logger.error(
                f"Security middleware error from {request.client.host} to {request.url.path}: {str(e)}"
            )
            raise


class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_string(input_string: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(input_string, str):
            return ""
        
        # Truncate if too long
        sanitized = input_string[:max_length]
        
        # HTML escape
        sanitized = html.escape(sanitized)
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        # Remove control characters except newline and tab
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')
        
        return sanitized.strip()
    
    @staticmethod
    def sanitize_email(email: str) -> str:
        """Sanitize email input"""
        if not isinstance(email, str):
            return ""
        
        # Basic email validation
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        
        if re.match(email_pattern, email):
            return email.lower().strip()
        
        return ""
    
    @staticmethod
    def sanitize_ip_address(ip: str) -> str:
        """Sanitize IP address input"""
        if not isinstance(ip, str):
            return ""
        
        # Remove whitespace
        ip = ip.strip()
        
        # Validate IP format
        if SecurityMiddleware._is_valid_ip(ip):
            return ip
        
        return ""
    
    @staticmethod
    def sanitize_hostname(hostname: str) -> str:
        """Sanitize hostname input"""
        if not isinstance(hostname, str):
            return ""
        
        # Remove whitespace and convert to lowercase
        hostname = hostname.strip().lower()
        
        # Hostname validation pattern
        hostname_pattern = r"^[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?)*$"
        
        if re.match(hostname_pattern, hostname) and len(hostname) <= 253:
            return hostname
        
        return ""