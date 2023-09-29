import os

MySQL_CONFIG = {
    "host": os.getenv('mysql_host'),
    "user": os.getenv('mysql_user'),
    "password": os.getenv('mysql_password'),
    "database": os.getenv('mysql_database')
}

# App Constants
SUPER_ADMIN = 'Super Admin'
ADMIN = 'Admin'
REQUIRED_ERROR = 'requiredError'
AUTH_ERROR ='authError'
API_FAILED_ERROR = 'apiFailedError'

# Network Constants
REQUEST_TIMEOUT = 60
