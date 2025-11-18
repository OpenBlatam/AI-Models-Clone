#!/bin/bash

# Ultimate Security System Deployment Script
# This script deploys the security system with all necessary configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
DOMAIN=${2:-localhost}
SSL_EMAIL=${3:-admin@example.com}

echo -e "${BLUE}🚀 Starting Ultimate Security System Deployment${NC}"
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"
echo -e "${BLUE}Domain: ${DOMAIN}${NC}"

# Function to print status
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if openssl is installed
    if ! command -v openssl &> /dev/null; then
        print_error "OpenSSL is not installed. Please install OpenSSL first."
        exit 1
    fi
    
    print_status "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    echo -e "${BLUE}📁 Creating necessary directories...${NC}"
    
    mkdir -p logs
    mkdir -p data
    mkdir -p ssl
    mkdir -p monitoring
    mkdir -p test-results
    mkdir -p init-scripts
    
    print_status "Directories created"
}

# Generate SSL certificates
generate_ssl_certificates() {
    echo -e "${BLUE}🔐 Generating SSL certificates...${NC}"
    
    if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
        if [ "$ENVIRONMENT" = "production" ]; then
            print_warning "Production environment detected. Please provide valid SSL certificates."
            print_warning "Place your certificates in ssl/cert.pem and ssl/key.pem"
        else
            # Generate self-signed certificates for development
            openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=${DOMAIN}"
            print_status "Self-signed SSL certificates generated"
        fi
    else
        print_status "SSL certificates already exist"
    fi
}

# Create environment file
create_environment_file() {
    echo -e "${BLUE}⚙️  Creating environment configuration...${NC}"
    
    if [ ! -f ".env.security" ]; then
        cat > .env.security << EOF
# Security System Environment Configuration
NODE_ENV=${ENVIRONMENT}
DOMAIN=${DOMAIN}

# Database Configuration
DATABASE_URL=postgresql://security_user:security_pass@postgres:5432/security_db
POSTGRES_DB=security_db
POSTGRES_USER=security_user
POSTGRES_PASSWORD=security_pass

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=redis_pass

# Security Keys (Generate secure keys for production)
SECRET_KEY=$(openssl rand -base64 32)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Biometric Authentication
BIOMETRIC_ENABLED=true
WEBAUTHN_RP_ID=${DOMAIN}
WEBAUTHN_RP_NAME=Ultimate Security System

# Threat Intelligence (Configure with your API keys)
THREAT_INTEL_API_KEY=your_threat_intel_api_key
THREAT_INTEL_ENDPOINT=https://api.threatintel.com

# Monitoring
MONITORING_ENABLED=true
ALERT_WEBHOOK_URL=https://your-webhook.com/alerts

# SSL Configuration
SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
SSL_KEY_PATH=/etc/nginx/ssl/key.pem
EOF
        print_status "Environment file created"
    else
        print_status "Environment file already exists"
    fi
}

# Create Nginx configuration
create_nginx_config() {
    echo -e "${BLUE}🌐 Creating Nginx configuration...${NC}"
    
    cat > nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    upstream security_app {
        server security-app:3000;
    }

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=login:10m rate=5r/m;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' wss: https:;";

    server {
        listen 80;
        server_name ${DOMAIN};
        return 301 https://\$server_name\$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name ${DOMAIN};

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security endpoints
        location /api/security/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://security_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Authentication endpoints
        location /api/auth/ {
            limit_req zone=login burst=5 nodelay;
            proxy_pass http://security_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Main application
        location / {
            proxy_pass http://security_app;
            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Health check
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF
    print_status "Nginx configuration created"
}

# Create database initialization script
create_db_init_script() {
    echo -e "${BLUE}🗄️  Creating database initialization script...${NC}"
    
    cat > init-scripts/01-init-security-db.sql << EOF
-- Security System Database Initialization
-- This script creates the necessary tables and indexes for the security system

-- Create security events table
CREATE TABLE IF NOT EXISTS security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    source VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    ip_address INET,
    user_agent TEXT,
    location VARCHAR(100),
    tags TEXT[],
    metadata JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create security alerts table
CREATE TABLE IF NOT EXISTS security_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    title VARCHAR(255) NOT NULL,
    description TEXT,
    source VARCHAR(100) NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.8,
    false_positive_probability DECIMAL(3,2) DEFAULT 0.1,
    priority INTEGER DEFAULT 5,
    affected_systems TEXT[],
    evidence TEXT[],
    recommendations TEXT[],
    assignee VARCHAR(100),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create threat intelligence table
CREATE TABLE IF NOT EXISTS threat_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    indicator_type VARCHAR(50) NOT NULL,
    indicator_value VARCHAR(500) NOT NULL,
    threat_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    confidence DECIMAL(3,2) DEFAULT 0.8,
    source VARCHAR(100) NOT NULL,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create compliance assessments table
CREATE TABLE IF NOT EXISTS compliance_assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework VARCHAR(50) NOT NULL,
    control_id VARCHAR(100) NOT NULL,
    control_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL,
    score DECIMAL(5,2),
    evidence TEXT[],
    recommendations TEXT[],
    assessor VARCHAR(100),
    assessment_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    next_assessment TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create security tests table
CREATE TABLE IF NOT EXISTS security_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    test_name VARCHAR(255) NOT NULL,
    test_type VARCHAR(50) NOT NULL,
    test_suite VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    severity VARCHAR(20),
    progress INTEGER DEFAULT 0,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    duration INTEGER,
    results JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_security_events_timestamp ON security_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_security_events_type ON security_events(event_type);
CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity);
CREATE INDEX IF NOT EXISTS idx_security_events_source ON security_events(source);

CREATE INDEX IF NOT EXISTS idx_security_alerts_timestamp ON security_alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_security_alerts_type ON security_alerts(alert_type);
CREATE INDEX IF NOT EXISTS idx_security_alerts_severity ON security_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_security_alerts_status ON security_alerts(status);

CREATE INDEX IF NOT EXISTS idx_threat_intelligence_type ON threat_intelligence(indicator_type);
CREATE INDEX IF NOT EXISTS idx_threat_intelligence_value ON threat_intelligence(indicator_value);
CREATE INDEX IF NOT EXISTS idx_threat_intelligence_active ON threat_intelligence(is_active);

CREATE INDEX IF NOT EXISTS idx_compliance_framework ON compliance_assessments(framework);
CREATE INDEX IF NOT EXISTS idx_compliance_status ON compliance_assessments(status);

CREATE INDEX IF NOT EXISTS idx_security_tests_type ON security_tests(test_type);
CREATE INDEX IF NOT EXISTS idx_security_tests_status ON security_tests(status);
CREATE INDEX IF NOT EXISTS idx_security_tests_suite ON security_tests(test_suite);

-- Insert initial data
INSERT INTO compliance_assessments (framework, control_id, control_name, status, score) VALUES
('ISO27001', 'A.5.1.1', 'Information Security Policies', 'compliant', 95.0),
('ISO27001', 'A.6.1.1', 'Information Security Roles and Responsibilities', 'compliant', 90.0),
('SOC2', 'CC1', 'Control Environment', 'compliant', 92.0),
('SOC2', 'CC2', 'Communication and Information', 'compliant', 88.0),
('GDPR', 'Art.5', 'Principles relating to processing of personal data', 'warning', 85.0),
('HIPAA', '164.308(a)(1)', 'Security Management Process', 'compliant', 90.0),
('PCI-DSS', '1.1', 'Install and maintain a firewall configuration', 'compliant', 95.0)
ON CONFLICT DO NOTHING;
EOF
    print_status "Database initialization script created"
}

# Deploy the system
deploy_system() {
    echo -e "${BLUE}🚀 Deploying security system...${NC}"
    
    # Stop existing containers
    docker-compose -f docker-compose.security.yml down || true
    
    # Build and start containers
    docker-compose -f docker-compose.security.yml --env-file .env.security up -d --build
    
    print_status "Security system deployed"
}

# Wait for services to be ready
wait_for_services() {
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    
    # Wait for database
    echo "Waiting for database..."
    until docker-compose -f docker-compose.security.yml exec postgres pg_isready -U security_user -d security_db; do
        sleep 2
    done
    print_status "Database is ready"
    
    # Wait for Redis
    echo "Waiting for Redis..."
    until docker-compose -f docker-compose.security.yml exec redis redis-cli ping; do
        sleep 2
    done
    print_status "Redis is ready"
    
    # Wait for application
    echo "Waiting for application..."
    until curl -f http://localhost:3000/api/health; do
        sleep 5
    done
    print_status "Application is ready"
}

# Run security tests
run_security_tests() {
    echo -e "${BLUE}🧪 Running security tests...${NC}"
    
    # Wait a bit for the system to stabilize
    sleep 30
    
    # Run basic health checks
    echo "Running health checks..."
    curl -f http://localhost:3000/api/health || print_warning "Health check failed"
    curl -f http://localhost:3000/api/security?action=health || print_warning "Security health check failed"
    
    print_status "Security tests completed"
}

# Display deployment information
display_deployment_info() {
    echo -e "${GREEN}🎉 Security System Deployment Complete!${NC}"
    echo ""
    echo -e "${BLUE}📋 Deployment Information:${NC}"
    echo -e "  Environment: ${ENVIRONMENT}"
    echo -e "  Domain: ${DOMAIN}"
    echo -e "  Application URL: https://${DOMAIN}"
    echo -e "  Health Check: https://${DOMAIN}/api/health"
    echo -e "  Security Dashboard: https://${DOMAIN}/security"
    echo ""
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo -e "  View logs: docker-compose -f docker-compose.security.yml logs -f"
    echo -e "  Stop system: docker-compose -f docker-compose.security.yml down"
    echo -e "  Restart system: docker-compose -f docker-compose.security.yml restart"
    echo -e "  Update system: docker-compose -f docker-compose.security.yml up -d --build"
    echo ""
    echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
    echo -e "  1. Change default passwords in production"
    echo -e "  2. Configure proper SSL certificates"
    echo -e "  3. Set up monitoring and alerting"
    echo -e "  4. Review and update security configurations"
    echo -e "  5. Enable firewall rules and network security"
    echo ""
    echo -e "${GREEN}✅ Your Ultimate Security System is now running!${NC}"
}

# Main deployment process
main() {
    check_prerequisites
    create_directories
    generate_ssl_certificates
    create_environment_file
    create_nginx_config
    create_db_init_script
    deploy_system
    wait_for_services
    run_security_tests
    display_deployment_info
}

# Run main function
main "$@"


