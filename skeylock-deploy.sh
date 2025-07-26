#!/bin/bash

# SkeyLock by Udar Soft - Production Deployment Script for Ubuntu 22.04
# Run as skeylock user: bash skeylock-deploy.sh

set -e

echo "🚀 SkeyLock by Udar Soft - Production Deployment"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
DOMAIN="skeylock.com"
APP_DIR="/opt/skeylock"
REPO_URL="https://github.com/dogukanakbas/SkeyLock.git"

# Check if running as skeylock user
if [[ $(whoami) != "skeylock" ]]; then
    print_error "This script should be run as 'skeylock' user"
    print_status "Switch to skeylock user: sudo su - skeylock"
    exit 1
fi

# 1. Clone or update repository
print_status "Setting up SkeyLock repository..."
if [ -d "$APP_DIR/SkeyLock" ]; then
    print_status "Updating existing repository..."
    cd $APP_DIR/SkeyLock
    git pull origin main
else
    print_status "Cloning SkeyLock repository..."
    cd $APP_DIR
    git clone $REPO_URL
    cd SkeyLock
fi
print_success "Repository ready"

# 2. Setup environment file
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.production .env
    print_warning "Environment file created from template"
    print_warning "Please edit .env file with your actual values:"
    print_warning "  - Database passwords"
    print_warning "  - JWT secret"
    print_warning "  - Stripe keys"
    print_warning "  - Email configuration"
    echo ""
    read -p "Press Enter to edit .env file now, or Ctrl+C to exit and edit manually..."
    nano .env
else
    print_success "Environment file already exists"
fi

# 3. Generate secure passwords if needed
print_status "Checking for placeholder passwords..."
if grep -q "CHANGE_THIS" .env; then
    print_warning "Found placeholder passwords. Generating secure ones..."
    
    # Generate secure passwords
    DB_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
    REDIS_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
    JWT_SECRET=$(openssl rand -base64 32)
    GRAFANA_PASSWORD=$(openssl rand -base64 12 | tr -d "=+/" | cut -c1-12)
    
    # Replace in .env file
    sed -i "s/CHANGE_THIS_STRONG_PASSWORD/$DB_PASSWORD/g" .env
    sed -i "s/CHANGE_THIS_REDIS_PASSWORD/$REDIS_PASSWORD/g" .env
    sed -i "s/CHANGE_THIS_TO_SUPER_SECURE_256_BIT_KEY/$JWT_SECRET/g" .env
    sed -i "s/CHANGE_THIS_GRAFANA_PASSWORD/$GRAFANA_PASSWORD/g" .env
    
    print_success "Secure passwords generated and applied"
    print_warning "Please save these passwords securely:"
    echo "Database Password: $DB_PASSWORD"
    echo "Redis Password: $REDIS_PASSWORD"
    echo "Grafana Password: $GRAFANA_PASSWORD"
    echo ""
fi

# 4. Check SSL certificates
print_status "Checking SSL certificates..."
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    print_warning "SSL certificates not found"
    print_status "Generating self-signed certificates for testing..."
    
    mkdir -p nginx/ssl
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=TR/ST=Istanbul/L=Istanbul/O=Udar Soft/CN=$DOMAIN"
    
    openssl dhparam -out nginx/ssl/dhparam.pem 2048
    
    print_success "Self-signed certificates generated"
    print_warning "For production, replace with Let's Encrypt certificates:"
    print_warning "sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN -d app.$DOMAIN -d api.$DOMAIN"
else
    print_success "SSL certificates found"
fi

# 5. Build and start services
print_status "Building and starting SkeyLock services..."
docker-compose down --remove-orphans 2>/dev/null || true
docker-compose pull
docker-compose build --no-cache
docker-compose up -d

print_success "SkeyLock services started"

# 6. Wait for services to be ready
print_status "Waiting for services to initialize..."
sleep 30

# 7. Check service health
print_status "Checking service health..."
services=("postgres" "redis" "backend" "frontend" "marketing" "nginx")
all_healthy=true

for service in "${services[@]}"; do
    if docker-compose ps $service | grep -q "Up"; then
        print_success "$service: Running"
    else
        print_error "$service: Not running"
        all_healthy=false
    fi
done

# 8. Test API endpoints
print_status "Testing API endpoints..."
if curl -f http://localhost:8002/health > /dev/null 2>&1; then
    print_success "Backend API: Responding"
else
    print_warning "Backend API: Not responding (may need more time)"
fi

if curl -f http://localhost > /dev/null 2>&1; then
    print_success "Frontend: Responding"
else
    print_warning "Frontend: Not responding (may need more time)"
fi

# 9. Setup log monitoring
print_status "Setting up log monitoring..."
mkdir -p /var/log/skeylock
docker-compose logs --tail=50 > /var/log/skeylock/deployment.log 2>&1
print_success "Logs saved to /var/log/skeylock/deployment.log"

# 10. Create backup script
print_status "Creating backup script..."
cat > /opt/skeylock/backup.sh << 'EOF'
#!/bin/bash
# SkeyLock Backup Script

BACKUP_DIR="/var/backups/skeylock"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/opt/skeylock/SkeyLock"

mkdir -p $BACKUP_DIR

# Backup database
cd $APP_DIR
docker-compose exec -T postgres pg_dump -U skeylock_user skeylock_production > $BACKUP_DIR/database_$DATE.sql

# Backup application files
tar -czf $BACKUP_DIR/app_$DATE.tar.gz -C /opt/skeylock SkeyLock --exclude='node_modules' --exclude='.git'

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/skeylock/backup.sh
print_success "Backup script created"

# 11. Setup cron job for backups
print_status "Setting up automated backups..."
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/skeylock/backup.sh >> /var/log/skeylock/backup.log 2>&1") | crontab -
print_success "Daily backup scheduled at 2 AM"

# 12. Final status report
echo ""
print_success "🎉 SkeyLock Deployment Complete!"
echo ""
echo "📊 Service Status:"
echo "=================="
docker-compose ps
echo ""
echo "🌐 Access URLs:"
echo "==============="
echo "Marketing Site: http://$DOMAIN (https after SSL setup)"
echo "Web Application: http://app.$DOMAIN"
echo "API Backend: http://api.$DOMAIN"
echo "Monitoring: http://monitoring.$DOMAIN"
echo ""
echo "📁 Important Paths:"
echo "=================="
echo "Application: $APP_DIR/SkeyLock"
echo "Logs: /var/log/skeylock/"
echo "Backups: /var/backups/skeylock/"
echo "SSL Certificates: $APP_DIR/SkeyLock/nginx/ssl/"
echo ""
echo "🔧 Management Commands:"
echo "======================"
echo "View logs: docker-compose logs -f"
echo "Restart services: docker-compose restart"
echo "Stop services: docker-compose down"
echo "Update application: git pull && docker-compose up -d --build"
echo "Manual backup: /opt/skeylock/backup.sh"
echo ""
echo "🔒 Security Reminders:"
echo "====================="
echo "1. Setup Let's Encrypt SSL certificates"
echo "2. Configure Stripe with live keys"
echo "3. Setup SendGrid for email"
echo "4. Configure monitoring alerts"
echo "5. Test backup and restore procedures"
echo ""

if [ "$all_healthy" = true ]; then
    print_success "All services are running successfully! 🚀"
    echo ""
    echo "🎯 Next Steps:"
    echo "============="
    echo "1. Configure DNS records for $DOMAIN"
    echo "2. Get SSL certificates: sudo certbot certonly --standalone -d $DOMAIN"
    echo "3. Update .env with production Stripe keys"
    echo "4. Test the application thoroughly"
    echo "5. Launch your marketing campaign!"
else
    print_warning "Some services may need attention. Check logs with: docker-compose logs"
fi

echo ""
print_success "SkeyLock by Ud