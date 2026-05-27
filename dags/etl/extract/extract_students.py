import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from etl.config.db_config import LMS_DB_CONFIG, WAREHOUSE_CONFIG
import csv
import os

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
        
def extract_latest_student_data(engine, warehouse_engine):
    # 1. Get the last entered student_id from the Warehouse
    try:
        with warehouse_engine.connect() as conn:
            # We look for the max student_id already in the Warehouse
            result = conn.execute(text("SELECT MAX(student_id) FROM dim_student"))
            last_id = result.scalar()
            
            # If the table is empty, last_id will be None. Set it to 0.
            if last_id is None:
                last_id = 0
                
        print(f"Last student_id found in Warehouse: {last_id}")
        
    except Exception as e:
        print(f"Could not check last ID (maybe table doesn't exist yet): {e}")
        last_id = 0

    # 2. Fetch only data GREATER than the last_id from the source
    # We use a f-string or parameter to inject the last_id
    query = f"SELECT * FROM students WHERE id > {last_id}"
    
    print(f"Fetching new records from source where id > {last_id}...")
    df = pd.read_sql(query, engine)

    if df.empty:
        print("No new records to fetch.")
    else:
        print(f"Extracted {len(df)} new records.")

    return df

def extract_student_data():
    engine = check_lms_db_connection()
    warehouse_engine = check_lms_warehouse_connection()
    
    df =extract_latest_student_data(engine, warehouse_engine)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    root_dir = os.path.dirname(current_dir) 
    
    json_path = os.path.join(root_dir, "students_extract_data.json")
    print(f"Saving JSON to: {json_path}")
    df.to_json(json_path, orient='records', indent=4)

    print("Success! Check your folder now.")

    return json_path
