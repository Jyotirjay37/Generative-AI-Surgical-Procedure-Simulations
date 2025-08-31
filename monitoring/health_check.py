#!/usr/bin/env python3

import requests
import sys
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/health_check.log'),
        logging.StreamHandler()
    ]
)

def check_health():
    """Check the health of the surgical simulation platform"""
    try:
        # Get base URL from environment or use default
        base_url = os.environ.get('HEALTH_CHECK_URL', 'http://localhost:5000')
        
        # Check health endpoint
        response = requests.get(f'{base_url}/health', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'healthy':
                logging.info(f"✅ Application is healthy - {datetime.now()}")
                return True
            else:
                logging.error(f"❌ Application is unhealthy - {data.get('error', 'Unknown error')}")
                return False
        else:
            logging.error(f"❌ Health check failed with status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logging.error("❌ Cannot connect to application - connection refused")
        return False
    except requests.exceptions.Timeout:
        logging.error("❌ Health check timed out")
        return False
    except Exception as e:
        logging.error(f"❌ Health check failed: {e}")
        return False

def check_api_endpoints():
    """Check if API endpoints are responding"""
    try:
        base_url = os.environ.get('HEALTH_CHECK_URL', 'http://localhost:5000')
        
        # Test procedures endpoint
        response = requests.get(f'{base_url}/api/procedures', timeout=5)
        if response.status_code == 200:
            logging.info("✅ API endpoints are responding")
            return True
        else:
            logging.error(f"❌ API endpoints failed with status {response.status_code}")
            return False
            
    except Exception as e:
        logging.error(f"❌ API check failed: {e}")
        return False

def main():
    """Main health check function"""
    logging.info("Starting health check...")
    
    # Check application health
    app_healthy = check_health()
    
    # Check API endpoints
    api_healthy = check_api_endpoints()
    
    # Overall health status
    overall_healthy = app_healthy and api_healthy
    
    if overall_healthy:
        logging.info("🎉 All health checks passed!")
        sys.exit(0)
    else:
        logging.error("💥 Health checks failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
