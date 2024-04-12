# gunicorn.py

import os

# Define the path to the log directory
log_dir = '/var/log/gunicorn/'

# Ensure the log directory exists
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Define the paths to the log files
access_logfile = os.path.join(log_dir, 'access.log')
error_logfile = os.path.join(log_dir, 'error.log')

# Gunicorn configuration
bind = '127.0.0.1:8000'  # Example: Bind to localhost on port 8000
workers = 3  # Example: Use 3 worker processes
accesslog = access_logfile  # Set the path to the access log file
errorlog = error_logfile  # Set the path to the error log file