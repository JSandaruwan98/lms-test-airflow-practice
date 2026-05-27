from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

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

def check_lms_db_connection():
    try:
        user = LMS_DB_CONFIG['user']
        password = quote_plus(LMS_DB_CONFIG['password']) 
        host = LMS_DB_CONFIG['host']
        port = LMS_DB_CONFIG['port']
        db = LMS_DB_CONFIG['database']

        conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        engine = create_engine(conn_str)
        
        return engine
    except Exception as e:
        print(f"Database connection failed: {e}")
        
def check_lms_warehouse_connection():
    try:
        user = WAREHOUSE_CONFIG['user']
        password = quote_plus(WAREHOUSE_CONFIG['password']) 
        host = WAREHOUSE_CONFIG['host']
        port = WAREHOUSE_CONFIG['port']
        db = WAREHOUSE_CONFIG['database']

        conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
        engine = create_engine(conn_str)
        
        return engine
    except Exception as e:
        print(f"Database connection failed: {e}")