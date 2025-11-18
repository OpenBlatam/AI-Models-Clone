@echo off
REM Ultimate Security System Deployment Script for Windows
REM This script deploys the security system with all necessary configurations

setlocal enabledelayedexpansion

REM Configuration
set ENVIRONMENT=%1
if "%ENVIRONMENT%"=="" set ENVIRONMENT=production

set DOMAIN=%2
if "%DOMAIN%"=="" set DOMAIN=localhost

set SSL_EMAIL=%3
if "%SSL_EMAIL%"=="" set SSL_EMAIL=admin@example.com

echo 🚀 Starting Ultimate Security System Deployment
echo Environment: %ENVIRONMENT%
echo Domain: %DOMAIN%

REM Check prerequisites
echo 🔍 Checking prerequisites...

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    exit /b 1
)

where docker-compose >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    exit /b 1
)

echo ✅ Prerequisites check passed

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data
if not exist "ssl" mkdir ssl
if not exist "monitoring" mkdir monitoring
if not exist "test-results" mkdir test-results
if not exist "init-scripts" mkdir init-scripts
echo ✅ Directories created

REM Generate SSL certificates
echo 🔐 Generating SSL certificates...
if not exist "ssl\cert.pem" (
    if "%ENVIRONMENT%"=="production" (
        echo ⚠️  Production environment detected. Please provide valid SSL certificates.
        echo ⚠️  Place your certificates in ssl\cert.pem and ssl\key.pem
    ) else (
        echo Generating self-signed SSL certificates...
        REM Note: Windows doesn't have openssl by default, so we'll create placeholder files
        echo Placeholder SSL certificate > ssl\cert.pem
        echo Placeholder SSL key > ssl\key.pem
        echo ✅ Self-signed SSL certificates created (placeholders)
    )
) else (
    echo ✅ SSL certificates already exist
)

REM Create environment file
echo ⚙️  Creating environment configuration...
if not exist ".env.security" (
    (
        echo # Security System Environment Configuration
        echo NODE_ENV=%ENVIRONMENT%
        echo DOMAIN=%DOMAIN%
        echo.
        echo # Database Configuration
        echo DATABASE_URL=postgresql://security_user:security_pass@postgres:5432/security_db
        echo POSTGRES_DB=security_db
        echo POSTGRES_USER=security_user
        echo POSTGRES_PASSWORD=security_pass
        echo.
        echo # Redis Configuration
        echo REDIS_URL=redis://redis:6379
        echo REDIS_PASSWORD=redis_pass
        echo.
        echo # Security Keys ^(Generate secure keys for production^)
        echo SECRET_KEY=your-secret-key-change-in-production
        echo ENCRYPTION_KEY=your-encryption-key-change-in-production
        echo.
        echo # Biometric Authentication
        echo BIOMETRIC_ENABLED=true
        echo WEBAUTHN_RP_ID=%DOMAIN%
        echo WEBAUTHN_RP_NAME=Ultimate Security System
        echo.
        echo # Threat Intelligence ^(Configure with your API keys^)
        echo THREAT_INTEL_API_KEY=your_threat_intel_api_key
        echo THREAT_INTEL_ENDPOINT=https://api.threatintel.com
        echo.
        echo # Monitoring
        echo MONITORING_ENABLED=true
        echo ALERT_WEBHOOK_URL=https://your-webhook.com/alerts
        echo.
        echo # SSL Configuration
        echo SSL_CERT_PATH=/etc/nginx/ssl/cert.pem
        echo SSL_KEY_PATH=/etc/nginx/ssl/key.pem
    ) > .env.security
    echo ✅ Environment file created
) else (
    echo ✅ Environment file already exists
)

REM Create Nginx configuration
echo 🌐 Creating Nginx configuration...
(
    echo events {
    echo     worker_connections 1024;
    echo }
    echo.
    echo http {
    echo     upstream security_app {
    echo         server security-app:3000;
    echo     }
    echo.
    echo     # Rate limiting
    echo     limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    echo     limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;
    echo.
    echo     # Security headers
    echo     add_header X-Frame-Options DENY;
    echo     add_header X-Content-Type-Options nosniff;
    echo     add_header X-XSS-Protection "1; mode=block";
    echo     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    echo.
    echo     server {
    echo         listen 80;
    echo         server_name %DOMAIN%;
    echo         return 301 https://$server_name$request_uri;
    echo     }
    echo.
    echo     server {
    echo         listen 443 ssl http2;
    echo         server_name %DOMAIN%;
    echo.
    echo         # SSL configuration
    echo         ssl_certificate /etc/nginx/ssl/cert.pem;
    echo         ssl_certificate_key /etc/nginx/ssl/key.pem;
    echo         ssl_protocols TLSv1.2 TLSv1.3;
    echo.
    echo         # Security endpoints
    echo         location /api/security/ {
    echo             limit_req zone=api burst=20 nodelay;
    echo             proxy_pass http://security_app;
    echo             proxy_set_header Host $host;
    echo             proxy_set_header X-Real-IP $remote_addr;
    echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    echo             proxy_set_header X-Forwarded-Proto $scheme;
    echo         }
    echo.
    echo         # Main application
    echo         location / {
    echo             proxy_pass http://security_app;
    echo             proxy_set_header Host $host;
    echo             proxy_set_header X-Real-IP $remote_addr;
    echo             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    echo             proxy_set_header X-Forwarded-Proto $scheme;
    echo         }
    echo.
    echo         # Health check
    echo         location /health {
    echo             access_log off;
    echo             return 200 "healthy\n";
    echo             add_header Content-Type text/plain;
    echo         }
    echo     }
    echo }
) > nginx.conf
echo ✅ Nginx configuration created

REM Deploy the system
echo 🚀 Deploying security system...

REM Stop existing containers
docker-compose -f docker-compose.security.yml down 2>nul

REM Build and start containers
docker-compose -f docker-compose.security.yml --env-file .env.security up -d --build

echo ✅ Security system deployed

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...

REM Wait for application
echo Waiting for application...
timeout /t 30 /nobreak >nul

REM Test if application is responding
:test_loop
curl -f http://localhost:3000/api/health >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Application is ready
    goto :deployment_complete
) else (
    echo Still waiting for application...
    timeout /t 5 /nobreak >nul
    goto :test_loop
)

:deployment_complete
echo.
echo 🎉 Security System Deployment Complete!
echo.
echo 📋 Deployment Information:
echo   Environment: %ENVIRONMENT%
echo   Domain: %DOMAIN%
echo   Application URL: http://%DOMAIN%:3000
echo   Health Check: http://%DOMAIN%:3000/api/health
echo   Security Dashboard: http://%DOMAIN%:3000/security
echo.
echo 🔧 Management Commands:
echo   View logs: docker-compose -f docker-compose.security.yml logs -f
echo   Stop system: docker-compose -f docker-compose.security.yml down
echo   Restart system: docker-compose -f docker-compose.security.yml restart
echo   Update system: docker-compose -f docker-compose.security.yml up -d --build
echo.
echo ⚠️  Important Security Notes:
echo   1. Change default passwords in production
echo   2. Configure proper SSL certificates
echo   3. Set up monitoring and alerting
echo   4. Review and update security configurations
echo   5. Enable firewall rules and network security
echo.
echo ✅ Your Ultimate Security System is now running!

pause


