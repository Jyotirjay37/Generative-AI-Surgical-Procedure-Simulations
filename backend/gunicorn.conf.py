import multiprocessing
import os

# Server socket
bind = os.environ.get('BIND', "127.0.0.1:5000")
backlog = 2048

# Worker processes
workers = int(os.environ.get('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "sync"
worker_connections = int(os.environ.get('WORKER_CONNECTIONS', 1000))
timeout = int(os.environ.get('TIMEOUT', 30))
keepalive = 2

# Restart workers after this many requests
max_requests = int(os.environ.get('MAX_REQUESTS', 1000))
max_requests_jitter = int(os.environ.get('MAX_REQUESTS_JITTER', 50))

# Preload application
preload_app = True

# Logging
accesslog = os.environ.get('ACCESS_LOG', "logs/access.log")
errorlog = os.environ.get('ERROR_LOG', "logs/error.log")
loglevel = os.environ.get('LOG_LEVEL', "info")

# Process naming
proc_name = "surgical-simulation"

# User and group (set in production)
# user = "surgicalsim"
# group = "surgicalsim"

# SSL (for production)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
