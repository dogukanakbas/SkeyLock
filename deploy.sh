#!/bin/bash

# SkeyLock by Udar Soft - Production Deployment Script
set -e

echo "🚀 Starting SkeyLock by Udar Soft Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${DOMAIN:-"yourdomain.com"}
EMAIL=${EMAIL:-"admin@yourdomain.com"}
ENVIRONMENT=${ENVIRONMENT:-"production"}

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

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env.production exists
    if [[ ! -f .env.production ]]; then
        print_error ".env.production file not found. Please create it from .env.production.example"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Setup SSL certificates
setup_ssl() {
    print_status "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p nginx/ssl
    
    if [[ ! -f nginx/ssl/cert.pem ]] || [[ ! -f nginx/ssl/key.pem ]]; then
        print_warning "SSL certificates not found. Generating self-signed certificates for testing..."
        
        # Generate self-signed certificate (for testing only)
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
        
        # Generate DH parameters
        openssl dhparam -out nginx/ssl/dhparam.pem 2048
        
        print_warning "Self-signed certificates generated. Replace with real certificates for production!"
    else
        print_success "SSL certificates found"
    fi
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Copy production environment
    cp .env.production .env
    
    # Generate secure JWT secret if not set
    if grep -q "CHANGE_THIS_TO_SUPER_SECURE_256_BIT_KEY" .env; then
        JWT_SECRET=$(openssl rand -base64 32)
        sed -i "s/CHANGE_THIS_TO_SUPER_SECURE_256_BIT_KEY/${JWT_SECRET}/g" .env
        print_success "Generated secure JWT secret"
    fi
    
    # Generate secure database password if not set
    if grep -q "CHANGE_THIS_PASSWORD" .env; then
        DB_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/CHANGE_THIS_PASSWORD/${DB_PASSWORD}/g" .env
        print_success "Generated secure database password"
    fi
    
    # Generate secure Redis password if not set
    if grep -q "CHANGE_THIS_REDIS_PASSWORD" .env; then
        REDIS_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/CHANGE_THIS_REDIS_PASSWORD/${REDIS_PASSWORD}/g" .env
        print_success "Generated secure Redis password"
    fi
    
    print_success "Environment setup completed"
}

# Build and deploy
deploy_application() {
    print_status "Building and deploying application..."
    
    # Pull latest images
    docker-compose pull
    
    # Build custom images
    docker-compose build --no-cache
    
    # Start services
    docker-compose up -d
    
    print_success "Application deployed successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for database
    print_status "Waiting for database..."
    until docker-compose exec -T postgres pg_isready -U iot_prod_user -d iot_security_prod; do
        sleep 2
    done
    print_success "Database is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker-compose exec -T redis redis-cli ping; do
        sleep 2
    done
    print_success "Redis is ready"
    
    # Wait for backend
    print_status "Waiting for backend API..."
    until curl -f http://localhost:8002/health; do
        sleep 5
    done
    print_success "Backend API is ready"
    
    print_success "All services are ready"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Run Alembic migrations
    docker-compose exec backend alembic upgrade head
    
    print_success "Database migrations completed"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create Grafana admin password
    if grep -q "CHANGE_THIS_GRAFANA_PASSWORD" .env; then
        GRAFANA_PASSWORD=$(openssl rand -base64 12)
        sed -i "s/CHANGE_THIS_GRAFANA_PASSWORD/${GRAFANA_PASSWORD}/g" .env
        print_success "Generated Grafana admin password: ${GRAFANA_PASSWORD}"
    fi
    
    # Import Grafana dashboards
    sleep 10  # Wait for Grafana to start
    
    print_success "Monitoring setup completed"
}

# Create backup script
create_backup_script() {
    print_status "Creating backup script..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash
# Automated backup script for SkeyLock by Udar Soft

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="iot_security_backup_${DATE}.tar.gz"

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup database
docker-compose exec -T postgres pg_dump -U iot_prod_user iot_security_prod > ${BACKUP_DIR}/db_${DATE}.sql

# Backup application data
tar -czf ${BACKUP_DIR}/${BACKUP_FILE} \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.log' \
    .

# Keep only last 30 days of backups
find ${BACKUP_DIR} -name "iot_security_backup_*.tar.gz" -mtime +30 -delete
find ${BACKUP_DIR} -name "db_*.sql" -mtime +30 -delete

echo "SkeyLock backup completed: ${BACKUP_FILE}"
EOF
    
    chmod +x backup.sh
    print_success "Backup script created"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check all services
    services=("postgres" "redis" "backend" "frontend" "marketing" "nginx")
    
    for service in "${services[@]}"; do
        if docker-compose ps $service | grep -q "Up"; then
            print_success "$service is running"
        else
            print_error "$service is not running"
            exit 1
        fi
    done
    
    # Check API endpoints
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_success "Marketing site is accessible"
    else
        print_warning "Marketing site health check failed"
    fi
    
    if curl -f http://localhost:8002/health > /dev/null 2>&1; then
        print_success "Backend API is accessible"
    else
        print_error "Backend API health check failed"
        exit 1
    fi
    
    print_success "Health check completed"
}

# Display deployment info
display_info() {
    print_success "🎉 SkeyLock by Udar Soft deployed successfully!"
    echo ""
    echo "📋 SkeyLock Deployment Information:"
    echo "=================================="
    echo "🌐 Marketing Site: https://${DOMAIN}"
    echo "📱 SkeyLock App: https://app.${DOMAIN}"
    echo "🔧 API: https://api.${DOMAIN}"
    echo "📊 Monitoring: https://monitoring.${DOMAIN}/grafana"
    echo ""
    echo "🔐 Important Credentials:"
    echo "========================"
    echo "Database Password: $(grep POSTGRES_PASSWORD .env | cut -d'=' -f2)"
    echo "Redis Password: $(grep REDIS_PASSWORD .env | cut -d'=' -f2)"
    echo "JWT Secret: $(grep JWT_SECRET .env | cut -d'=' -f2)"
    echo "Grafana Password: $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"
    echo ""
    echo "⚠️  Security Reminders:"
    echo "======================"
    echo "1. Replace self-signed SSL certificates with real ones"
    echo "2. Update Stripe keys with production values"
    echo "3. Configure proper DNS records"
    echo "4. Set up automated backups"
    echo "5. Configure monitoring alerts"
    echo ""
    echo "📚 Next Steps:"
    echo "============="
    echo "1. Test all functionality"
    echo "2. Set up domain DNS records"
    echo "3. Configure real SSL certificates"
    echo "4. Update Stripe webhook URLs"
    echo "5. Set up monitoring alerts"
    echo ""
}

# Main deployment flow
main() {
    print_status "SkeyLock by Udar Soft - Production Deployment"
    echo "=============================================="
    
    check_prerequisites
    setup_ssl
    setup_environment
    deploy_application
    wait_for_services
    run_migrations
    setup_monitoring
    create_backup_script
    health_check
    display_info
    
    print_success "Deployment completed! 🚀"
}

# Run main function
main "$@"