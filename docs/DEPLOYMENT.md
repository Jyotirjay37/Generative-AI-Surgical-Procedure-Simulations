# Surgical Simulation Platform - Deployment Guide

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Development Setup](#development-setup)
4. [Production Deployment](#production-deployment)
5. [Docker Deployment](#docker-deployment)
6. [Cloud Deployment](#cloud-deployment)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Security Considerations](#security-considerations)
9. [Troubleshooting](#troubleshooting)
10. [Performance Optimization](#performance-optimization)

## Overview

This guide provides comprehensive instructions for deploying the Surgical Simulation Platform in various environments, from local development to production cloud deployments.

## System Requirements

### Minimum Requirements

- **OS**: Ubuntu 20.04+, CentOS 8+, or Windows Server 2019+
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4GB
- **Storage**: 20GB available space
- **Network**: Stable internet connection

### Recommended Requirements

- **OS**: Ubuntu 22.04 LTS
- **CPU**: 4+ cores, 3.0 GHz
- **RAM**: 8GB+
- **Storage**: 50GB+ SSD
- **Network**: High-speed internet connection

### Software Dependencies

- **Python**: 3.9+
- **Node.js**: 16+ (for frontend build tools)
- **Nginx**: 1.18+
- **PostgreSQL**: 13+ (optional, for production)
- **Redis**: 6+ (optional, for caching)

## Development Setup

### Local Development Environment

#### 1. Clone Repository

```bash
git clone https://github.com/your-org/surgical-simulation-platform.git
cd surgical-simulation-platform
```

#### 2. Python Environment Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Environment Configuration

Create `.env` file in the project root:

```env
# Flask Configuration
FLASK_APP=backend/app.py
FLASK_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///database/surgical_simulations.db

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Optional: External Services
REDIS_URL=redis://localhost:6379
```

#### 4. Database Initialization

```bash
cd backend
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.init_database()"
```

#### 5. Run Development Server

```bash
# From backend directory
python app.py

# Or using Flask CLI
flask run --host=0.0.0.0 --port=5000
```

#### 6. Access Application

- **Dashboard**: http://localhost:5000
- **API Documentation**: http://localhost:5000/api/procedures

### Development Tools

#### Code Quality

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run linting
flake8 backend/
black backend/

# Run tests
pytest tests/ -v

# Run type checking
mypy backend/
```

#### Database Management

```bash
# Initialize database
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.init_database()"

# Reset database
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.reset_database()"

# Backup database
cp database/surgical_simulations.db database/backup_$(date +%Y%m%d_%H%M%S).db
```

## Production Deployment

### Traditional Server Deployment

#### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv nginx git supervisor

# Create application user
sudo useradd -m -s /bin/bash surgicalsim
sudo usermod -aG sudo surgicalsim
```

#### 2. Application Setup

```bash
# Switch to application user
sudo su - surgicalsim

# Clone repository
git clone https://github.com/your-org/surgical-simulation-platform.git
cd surgical-simulation-platform

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs database backups
```

#### 3. Environment Configuration

Create production `.env` file:

```env
# Production Configuration
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-very-secure-production-secret-key

# Database Configuration
DATABASE_URL=sqlite:///database/surgical_simulations.db

# Server Configuration
HOST=127.0.0.1
PORT=5000

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

#### 4. Gunicorn Configuration

Create `backend/gunicorn.conf.py`:

```python
import multiprocessing

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Preload application
preload_app = True

# Logging
accesslog = "/opt/surgical-simulation-platform/logs/access.log"
errorlog = "/opt/surgical-simulation-platform/logs/error.log"
loglevel = "info"

# Process naming
proc_name = "surgical-simulation"

# User and group
user = "surgicalsim"
group = "surgicalsim"
```

#### 5. Systemd Service Configuration

Create `/etc/systemd/system/surgical-simulation.service`:

```ini
[Unit]
Description=Surgical Simulation Platform
After=network.target

[Service]
Type=notify
User=surgicalsim
Group=surgicalsim
WorkingDirectory=/home/surgicalsim/surgical-simulation-platform/backend
Environment=PATH=/home/surgicalsim/surgical-simulation-platform/venv/bin
Environment=FLASK_ENV=production
ExecStart=/home/surgicalsim/surgical-simulation-platform/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 6. Nginx Configuration

Create `/etc/nginx/sites-available/surgical-simulation`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

    # Static files
    location /static {
        alias /home/surgicalsim/surgical-simulation-platform/frontend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Proxy to Flask application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

#### 7. Enable and Start Services

```bash
# Enable nginx site
sudo ln -s /etc/nginx/sites-available/surgical-simulation /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Enable and start application service
sudo systemctl daemon-reload
sudo systemctl enable surgical-simulation
sudo systemctl start surgical-simulation

# Check status
sudo systemctl status surgical-simulation
```

#### 8. SSL Configuration (Optional)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add line: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Supervisor Configuration (Alternative)

Create `/etc/supervisor/conf.d/surgical-simulation.conf`:

```ini
[program:surgical-simulation]
command=/home/surgicalsim/surgical-simulation-platform/venv/bin/gunicorn --config gunicorn.conf.py app:app
directory=/home/surgicalsim/surgical-simulation-platform/backend
user=surgicalsim
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/surgicalsim/surgical-simulation-platform/logs/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=10
environment=FLASK_ENV="production"
stopasgroup=true
killasgroup=true
```

## Docker Deployment

### Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=backend/app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p logs database backups

# Create non-root user
RUN useradd -m -s /bin/bash surgicalsim && \
    chown -R surgicalsim:surgicalsim /app
USER surgicalsim

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--config", "backend/gunicorn.conf.py", "backend.app:app"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=sqlite:///database/surgical_simulations.db
    volumes:
      - ./database:/app/database
      - ./logs:/app/logs
      - ./backups:/app/backups
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./deployment/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./frontend/static:/usr/share/nginx/html/static
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Docker Deployment Commands

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale web service
docker-compose up -d --scale web=3

# Stop services
docker-compose down

# Update application
git pull
docker-compose build
docker-compose up -d
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup

```bash
# Launch EC2 instance (Ubuntu 22.04 LTS)
# Instance type: t3.medium or larger
# Security group: Allow ports 22, 80, 443

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 2. Application Deployment

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3 python3-pip python3-venv nginx git

# Clone application
git clone https://github.com/your-org/surgical-simulation-platform.git
cd surgical-simulation-platform

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure application
cp .env.example .env
# Edit .env with production values
```

#### 3. AWS-Specific Configuration

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
```

#### 4. Load Balancer Setup

```bash
# Create Application Load Balancer
# Target Group: EC2 instances
# Health Check: /health endpoint
# SSL Certificate: ACM certificate
```

### Google Cloud Platform Deployment

#### 1. App Engine Deployment

Create `app.yaml`:

```yaml
runtime: python39
entrypoint: gunicorn --config backend/gunicorn.conf.py backend.app:app

instance_class: F2

automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10

env_variables:
  FLASK_ENV: production
  DATABASE_URL: sqlite:///database/surgical_simulations.db

handlers:
  - url: /static
    static_dir: frontend/static
    secure: always

  - url: /.*
    script: auto
    secure: always
```

Deploy:

```bash
# Install Google Cloud SDK
# Initialize project
gcloud init

# Deploy to App Engine
gcloud app deploy
```

#### 2. Cloud Run Deployment

```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/surgical-simulation

# Deploy to Cloud Run
gcloud run deploy surgical-simulation \
  --image gcr.io/PROJECT_ID/surgical-simulation \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure Deployment

#### 1. Azure App Service

```bash
# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name surgical-sim-rg --location eastus

# Create app service plan
az appservice plan create --name surgical-sim-plan --resource-group surgical-sim-rg --sku B1

# Create web app
az webapp create --name surgical-simulation --resource-group surgical-sim-rg --plan surgical-sim-plan --runtime "PYTHON|3.9"

# Deploy application
az webapp deployment source config-local-git --name surgical-simulation --resource-group surgical-sim-rg
```

## Monitoring and Maintenance

### Health Monitoring

#### Health Check Endpoint

Add to `backend/app.py`:

```python
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db_manager.get_connection()
        
        # Check application status
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500
```

#### Monitoring Script

Create `monitoring/health_check.py`:

```python
#!/usr/bin/env python3

import requests
import sys
import logging
from datetime import datetime

def check_health():
    try:
        response = requests.get('http://localhost:5000/health', timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'healthy':
                print(f"✅ Application is healthy - {datetime.now()}")
                return True
            else:
                print(f"❌ Application is unhealthy - {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if not check_health():
        sys.exit(1)
```

### Log Management

#### Log Rotation

Create `/etc/logrotate.d/surgical-simulation`:

```
/home/surgicalsim/surgical-simulation-platform/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 surgicalsim surgicalsim
    postrotate
        systemctl reload surgical-simulation
    endscript
}
```

#### Log Monitoring

```bash
# Monitor application logs
tail -f /home/surgicalsim/surgical-simulation-platform/logs/app.log

# Monitor nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Monitor system logs
journalctl -u surgical-simulation -f
```

### Backup Strategy

#### Database Backup

Create `backup/backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/home/surgicalsim/surgical-simulation-platform/backups"
DB_PATH="/home/surgicalsim/surgical-simulation-platform/database/surgical_simulations.db"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
cp $DB_PATH $BACKUP_DIR/surgical_sim_$DATE.db

# Compress backup
gzip $BACKUP_DIR/surgical_sim_$DATE.db

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.db.gz" -mtime +30 -delete

echo "Backup completed: surgical_sim_$DATE.db.gz"
```

#### Automated Backups

```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /home/surgicalsim/surgical-simulation-platform/backup/backup.sh
```

### Performance Monitoring

#### Resource Monitoring

```bash
# Monitor system resources
htop
iotop
nethogs

# Monitor application performance
ps aux | grep gunicorn
netstat -tlnp | grep 5000
```

#### Application Metrics

Add metrics endpoint to `backend/app.py`:

```python
@app.route('/metrics')
def metrics():
    import psutil
    
    return jsonify({
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "active_connections": len(psutil.net_connections()),
        "uptime": time.time() - psutil.boot_time()
    })
```

## Security Considerations

### Security Headers

Add security middleware to `backend/app.py`:

```python
from flask_talisman import Talisman

# Configure security headers
Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline'",
        'style-src': "'self' 'unsafe-inline'",
        'img-src': "'self' data: https:",
    },
    force_https=False  # Set to True in production
)
```

### Environment Security

```bash
# Secure environment file
chmod 600 .env

# Secure application directory
chmod 755 /home/surgicalsim/surgical-simulation-platform
chmod 644 /home/surgicalsim/surgical-simulation-platform/.env

# Secure logs
chmod 644 /home/surgicalsim/surgical-simulation-platform/logs/*
```

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### SSL/TLS Configuration

```nginx
# Enhanced SSL configuration in nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
ssl_prefer_server_ciphers off;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

## Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check logs
sudo journalctl -u surgical-simulation -n 50

# Check port availability
sudo netstat -tlnp | grep 5000

# Check permissions
ls -la /home/surgicalsim/surgical-simulation-platform/

# Test application manually
cd /home/surgicalsim/surgical-simulation-platform/backend
source ../venv/bin/activate
python app.py
```

#### Database Issues

```bash
# Check database file
ls -la /home/surgicalsim/surgical-simulation-platform/database/

# Test database connection
cd /home/surgicalsim/surgical-simulation-platform/backend
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); print(db.get_connection())"

# Reset database if needed
python -c "from database_manager import DatabaseManager; db = DatabaseManager(); db.reset_database()"
```

#### Nginx Issues

```bash
# Check nginx configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

#### Performance Issues

```bash
# Check system resources
free -h
df -h
top

# Check application processes
ps aux | grep gunicorn

# Monitor network connections
netstat -an | grep :5000 | wc -l
```

### Debug Mode

Enable debug mode temporarily:

```bash
# Edit .env file
FLASK_ENV=development
DEBUG=True

# Restart application
sudo systemctl restart surgical-simulation
```

### Recovery Procedures

#### Application Recovery

```bash
# Stop application
sudo systemctl stop surgical-simulation

# Backup current state
cp -r /home/surgicalsim/surgical-simulation-platform /home/surgicalsim/backup_$(date +%Y%m%d_%H%M%S)

# Restore from backup or redeploy
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Start application
sudo systemctl start surgical-simulation
```

#### Database Recovery

```bash
# Stop application
sudo systemctl stop surgical-simulation

# Restore database from backup
cp /home/surgicalsim/surgical-simulation-platform/backups/surgical_sim_YYYYMMDD_HHMMSS.db.gz /tmp/
gunzip /tmp/surgical_sim_YYYYMMDD_HHMMSS.db.gz
cp /tmp/surgical_sim_YYYYMMDD_HHMMSS.db /home/surgicalsim/surgical-simulation-platform/database/surgical_simulations.db

# Start application
sudo systemctl start surgical-simulation
```

## Performance Optimization

### Application Optimization

#### Gunicorn Tuning

```python
# Optimize gunicorn.conf.py
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
```

#### Database Optimization

```python
# Add database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### Caching Strategy

#### Redis Caching

```python
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            result = redis_client.get(cache_key)
            if result:
                return json.loads(result)
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, expire_time, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### CDN Configuration

#### Static File Optimization

```nginx
# Nginx static file optimization
location /static {
    alias /home/surgicalsim/surgical-simulation-platform/frontend/static;
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary Accept-Encoding;
    gzip_static on;
    access_log off;
}
```

### Load Balancing

#### Multiple Application Instances

```bash
# Scale application instances
sudo systemctl stop surgical-simulation
sudo cp /etc/systemd/system/surgical-simulation.service /etc/systemd/system/surgical-simulation@.service

# Edit service file to use %i for instance number
# Start multiple instances
sudo systemctl start surgical-simulation@1
sudo systemctl start surgical-simulation@2
sudo systemctl start surgical-simulation@3
```

#### Nginx Load Balancing

```nginx
upstream surgical_sim_backend {
    server 127.0.0.1:5001;
    server 127.0.0.1:5002;
    server 127.0.0.1:5003;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://surgical_sim_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Conclusion

This deployment guide provides comprehensive instructions for deploying the Surgical Simulation Platform in various environments. Choose the deployment method that best fits your requirements and infrastructure.

For additional support:
- Check the troubleshooting section
- Review application logs
- Contact the development team
- Refer to the API documentation

Remember to regularly update the application and monitor its performance to ensure optimal operation.
