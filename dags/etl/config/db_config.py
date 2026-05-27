# config/db_config.py

# Source Database (LMS)
LMS_DB_CONFIG = {
    "host": "localhost", # or Azure Private IP
    "database": "lms_db",
    "user": "user_admin",
    "password": "Asdf@1234",
    "port": 5432
}

# Destination Database (Warehouse)
WAREHOUSE_CONFIG = {
    "host": "localhost",
    "database": "lms_warehouse",
    "user": "user_admin",
    "password": "Asdf@1234",
    "port": 5432
}