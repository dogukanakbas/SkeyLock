#!/bin/bash

# SkeyLock by Udar Soft - Ubuntu 22.04 Server Setup Script
# Run as: sudo bash server-setup.sh

set -e

echo "🚀 SkeyLock by Udar Soft - Ubuntu 22.04 Server Setup"
echo "=================================================="

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

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# 1. System Update
print_status "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated successfully"

# 2. Install Essential Packages
print_status "Installing essential packages..."
apt install -y \
    curl \
    wget \
    git \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release \
    ufw \
    fail2ban \
    htop \
    nano \
    vim \
    tree \
    net-tools \
    openssl
print_success "Essential packages installed"

# 3. Install Docker
print_status "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker
systemctl start docker
print_success "Docker installed and started"

# 4. Install Docker Compose (standalone)
print_status "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
print_success "Docker Compose installed"

# 5. Install Node.js (for development/testing)
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
print_success "Node.js installed: $(node --version)"

# 6. Install Python (for scripts)
print_status "Installing Python..."
apt install -y python3 python3-pip python3-venv
print_success "Python installed: $(python3 --version)"

# 7. Install Certbot (Let's Encrypt)
print_status "Installing Certbot for SSL certificates..."
apt install -y certbot python3-certbot-nginx
print_success "Certbot installed"

# 8. Install Nginx (backup/standalone option)
print_status "Installing Nginx..."
apt install -y nginx
systemctl enable nginx
systemctl stop nginx  # We'll use Docker nginx
print_success "Nginx installed (stopped - using Docker version)"

# 9. Configure Firewall
print_status "Configuring UFW firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw --force enable
print_success "Firewall configured"

# 10. Configure Fail2Ban
print_status "Configuring Fail2Ban..."
systemctl enable fail2ban
systemctl start fail2ban
print_success "Fail2Ban configured"

# 11. Create SkeyLock user
print_status "Creating skeylock user..."
if ! id "skeylock" &>/dev/null; then
    useradd -m -s /bin/bash skeylock
    usermod -aG docker skeylock
    usermod -aG sudo skeylock
    print_success "User 'skeylock' created and added to docker group"
else
    print_warning "User 'skeylock' already exists"
fi

# 12. Create directories
print_status "Creating application directories..."
mkdir -p /opt/skeylock
mkdir -p /var/log/skeylock
mkdir -p /var/backups/skeylock
chown -R skeylock:skeylock /opt/skeylock
chown -R skeylock:skeylock /var/log/skeylock
chown -R skeylock:skeylock /var/backups/skeylock
print_success "Directories created"

# 13. Configure system limits
print_status "Configuring system limits..."
cat >> /etc/security/limits.conf << EOF
# SkeyLock limits
skeylock soft nofile 65536
skeylock hard nofile 65536
skeylock soft nproc 4096
skeylock hard nproc 4096
EOF
print_success "System limits configured"

# 14. Configure sysctl for production
print_status "Configuring sysctl for production..."
cat >> /etc/sysctl.conf << EOF
# SkeyLock production settings
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.ip_local_port_range = 1024 65535
net.ipv4.tcp_fin_timeout = 30
vm.swappiness = 10
EOF
sysctl -p
print_success "Sysctl configured"

# 15. Install monitoring tools
print_status "Installing monitoring tools..."
apt install -y htop iotop nethogs ncdu
print_success "Monitoring tools installed"

# 16. Setup log rotation
print_status "Setting up log rotation..."
cat > /etc/logrotate.d/skeylock << EOF
/var/log/skeylock/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 skeylock skeylock
    postrotate
        systemctl reload docker || true
    endscript
}
EOF
print_success "Log rotation configured"

# 17. Create swap file (if not exists)
print_status "Checking swap configuration..."
if ! swapon --show | grep -q "/swapfile"; then
    print_status "Creating 2GB swap file..."
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
    print_success "Swap file created and enabled"
else
    print_success "Swap already configured"
fi

# 18. Install Git LFS (for large files)
print_status "Installing Git LFS..."
curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash
apt install -y git-lfs
print_success "Git LFS installed"

# 19. Configure timezone
print_status "Setting timezone to UTC..."
timedatectl set-timezone UTC
print_success "Timezone set to UTC"

# 20. Install additional security tools
print_status "Installing security tools..."
apt install -y rkhunter chkrootkit lynis
print_success "Security tools installed"

# Final system info
print_success "🎉 SkeyLock Server Setup Complete!"
echo ""
echo "📊 System Information:"
echo "====================="
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo "Docker: $(docker --version)"
echo "Docker Compose: $(docker-compose --version)"
echo "Node.js: $(node --version)"
echo "Python: $(python3 --version)"
echo "Nginx: $(nginx -v 2>&1)"
echo "Certbot: $(certbot --version)"
echo ""
echo "🔐 Security Status:"
echo "=================="
echo "UFW Firewall: $(ufw status | head -1)"
echo "Fail2Ban: $(systemctl is-active fail2ban)"
echo "Docker: $(systemctl is-active docker)"
echo ""
echo "📁 Directories Created:"
echo "======================"
echo "Application: /opt/skeylock"
echo "Logs: /var/log/skeylock"
echo "Backups: /var/backups/skeylock"
echo ""
echo "👤 User Account:"
echo "==============="
echo "Username: skeylock"
echo "Groups: $(groups skeylock)"
echo ""
echo "🚀 Next Steps:"
echo "============="
echo "1. Switch to skeylock user: sudo su - skeylock"
echo "2. Clone repository: git clone https://github.com/dogukanakbas/SkeyLock.git"
echo "3. Configure DNS for skeylock.com"
echo "4. Get SSL certificates: sudo certbot certonly --standalone -d skeylock.com"
echo "5. Deploy SkeyLock: ./deploy.sh"
echo ""
print_success "Server is ready for SkeyLock deployment! 🎉"