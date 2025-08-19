#!/bin/bash

# Production Deployment Script for Algorithmic Trading Platform
# This script sets up and deploys the complete trading platform

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="trading-platform"
DOMAIN="yourdomain.com"
EMAIL="admin@yourdomain.com"

echo -e "${BLUE}🚀 Starting Production Deployment for Algorithmic Trading Platform${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
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
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        print_error "Docker daemon is not running. Please start Docker first."
        exit 1
    fi
    
    print_status "Prerequisites check passed ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs/{backend,frontend,nginx}
    mkdir -p docker/ssl
    mkdir -p docker/grafana/provisioning/{datasources,dashboards}
    mkdir -p backups
    mkdir -p ssl
    
    print_status "Directories created ✓"
}

# Generate SSL certificates (self-signed for testing, use Let's Encrypt for production)
generate_ssl_certificates() {
    print_status "Generating SSL certificates..."
    
    if [ ! -f "docker/ssl/cert.pem" ] || [ ! -f "docker/ssl/key.pem" ]; then
        print_warning "Generating self-signed SSL certificates for testing..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout docker/ssl/key.pem \
            -out docker/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=$DOMAIN"
        
        print_status "Self-signed SSL certificates generated ✓"
        print_warning "For production, replace with Let's Encrypt certificates"
    else
        print_status "SSL certificates already exist ✓"
    fi
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f ".env.production" ]; then
        print_error ".env.production file not found. Please create it first."
        exit 1
    fi
    
    # Copy production env to .env
    cp .env.production .env
    
    # Generate secure passwords if not set
    if grep -q "your_secure_postgres_password_here" .env; then
        print_warning "Generating secure passwords..."
        
        # Generate PostgreSQL password
        POSTGRES_PASSWORD=$(openssl rand -base64 32)
        sed -i "s/your_secure_postgres_password_here/$POSTGRES_PASSWORD/g" .env
        
        # Generate Redis password
        REDIS_PASSWORD=$(openssl rand -base64 32)
        sed -i "s/your_secure_redis_password_here/$REDIS_PASSWORD/g" .env
        
        # Generate JWT secret
        SECRET_KEY=$(openssl rand -base64 64)
        sed -i "s/your_very_long_and_secure_secret_key_here_minimum_32_characters/$SECRET_KEY/g" .env
        
        # Generate Grafana password
        GRAFANA_PASSWORD=$(openssl rand -base64 16)
        sed -i "s/your_secure_grafana_password_here/$GRAFANA_PASSWORD/g" .env
        
        print_status "Secure passwords generated and saved to .env ✓"
    fi
    
    print_status "Environment variables configured ✓"
}

# Build and deploy services
deploy_services() {
    print_status "Building and deploying services..."
    
    # Stop existing services
    docker-compose -f docker-compose.prod.yml down --remove-orphans
    
    # Build images
    print_status "Building Docker images..."
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    # Start services
    print_status "Starting services..."
    docker-compose -f docker-compose.prod.yml up -d
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    check_service_health
    
    print_status "Services deployed successfully ✓"
}

# Check service health
check_service_health() {
    print_status "Checking service health..."
    
    # Check PostgreSQL
    if docker-compose -f docker-compose.prod.yml exec -T postgres pg_isready -U trading_user -d trading_platform > /dev/null 2>&1; then
        print_status "PostgreSQL: Healthy ✓"
    else
        print_error "PostgreSQL: Unhealthy ✗"
        return 1
    fi
    
    # Check Redis
    if docker-compose -f docker-compose.prod.yml exec -T redis redis-cli --raw incr ping > /dev/null 2>&1; then
        print_status "Redis: Healthy ✓"
    else
        print_error "Redis: Unhealthy ✗"
        return 1
    fi
    
    # Check Backend
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        print_status "Backend: Healthy ✓"
    else
        print_error "Backend: Unhealthy ✗"
        return 1
    fi
    
    # Check Frontend
    if curl -f http://localhost/health > /dev/null 2>&1; then
        print_status "Frontend: Healthy ✓"
    else
        print_error "Frontend: Unhealthy ✗"
        return 1
    fi
    
    print_status "All services are healthy ✓"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create Prometheus configuration
    cat > docker/prometheus.yml << EOF
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'trading-backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
EOF
    
    # Create Grafana datasource
    cat > docker/grafana/provisioning/datasources/datasource.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    print_status "Monitoring configured ✓"
}

# Setup backup script
setup_backup() {
    print_status "Setting up backup system..."
    
    cat > backup.sh << 'EOF'
#!/bin/bash

# Backup script for trading platform
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="trading_backup_$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup PostgreSQL
docker-compose -f docker-compose.prod.yml exec -T postgres pg_dump -U trading_user trading_platform > "$BACKUP_DIR/${BACKUP_NAME}.sql"

# Backup logs
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_logs.tar.gz" logs/

# Backup configuration
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" .env docker-compose.prod.yml docker/

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "trading_backup_*" -mtime +30 -delete

echo "Backup completed: $BACKUP_NAME"
EOF
    
    chmod +x backup.sh
    
    # Add to crontab if not already there
    if ! crontab -l 2>/dev/null | grep -q "backup.sh"; then
        (crontab -l 2>/dev/null; echo "0 2 * * * $(pwd)/backup.sh") | crontab -
        print_status "Backup scheduled for daily at 2 AM ✓"
    fi
    
    print_status "Backup system configured ✓"
}

# Setup firewall rules
setup_firewall() {
    print_status "Setting up firewall rules..."
    
    # Check if ufw is available
    if command -v ufw &> /dev/null; then
        # Allow SSH
        ufw allow ssh
        
        # Allow HTTP/HTTPS
        ufw allow 80/tcp
        ufw allow 443/tcp
        
        # Allow application ports
        ufw allow 8000/tcp  # Backend API
        ufw allow 3000/tcp  # Grafana
        ufw allow 9090/tcp  # Prometheus
        
        # Enable firewall
        ufw --force enable
        
        print_status "Firewall configured ✓"
    else
        print_warning "ufw not available, skipping firewall configuration"
    fi
}

# Display deployment information
display_deployment_info() {
    echo ""
    echo -e "${GREEN}🎉 Deployment Completed Successfully!${NC}"
    echo "=================================================="
    echo ""
    echo -e "${BLUE}Service URLs:${NC}"
    echo "  Frontend:     http://$DOMAIN"
    echo "  Backend API:  http://$DOMAIN:8000"
    echo "  Grafana:      http://$DOMAIN:3000"
    echo "  Prometheus:   http://$DOMAIN:9090"
    echo ""
    echo -e "${BLUE}Default Credentials:${NC}"
    echo "  Grafana Admin: admin / $(grep GRAFANA_PASSWORD .env | cut -d'=' -f2)"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Update DNS records to point to this server"
    echo "  2. Replace self-signed SSL certificates with Let's Encrypt"
    echo "  3. Configure exchange API keys in .env file"
    echo "  4. Set up monitoring alerts in Grafana"
    echo "  5. Test the platform with paper trading"
    echo ""
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "  View logs:        docker-compose -f docker-compose.prod.yml logs -f"
    echo "  Stop services:    docker-compose -f docker-compose.prod.yml down"
    echo "  Restart:          docker-compose -f docker-compose.prod.yml restart"
    echo "  Backup:           ./backup.sh"
    echo ""
}

# Main deployment function
main() {
    echo "Starting deployment at $(date)"
    
    check_prerequisites
    create_directories
    generate_ssl_certificates
    setup_environment
    setup_monitoring
    setup_backup
    deploy_services
    setup_firewall
    display_deployment_info
    
    echo "Deployment completed at $(date)"
}

# Run main function
main "$@"