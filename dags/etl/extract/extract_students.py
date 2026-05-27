import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from etl.config.db_config import LMS_DB_CONFIG
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

def extract_student_data():
    engine = check_lms_db_connection()
    
    query = "SELECT * FROM students" # Assuming students table exists
    df = pd.read_sql(query, engine)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    root_dir = os.path.dirname(current_dir) 
    
    json_path = os.path.join(root_dir, "students_extract_data.json")
    print(f"Saving JSON to: {json_path}")
    df.to_json(json_path, orient='records', indent=4)

    print("Success! Check your folder now.")

    return json_path
