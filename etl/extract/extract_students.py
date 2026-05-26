import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
from etl.config.db_config import LMS_DB_CONFIG

def extract_student_data():
    # Encode the password to handle special characters like '@'
    user = LMS_DB_CONFIG['user']
    password = quote_plus(LMS_DB_CONFIG['password']) # <--- Encode here
    host = LMS_DB_CONFIG['host']
    port = LMS_DB_CONFIG['port']
    db = LMS_DB_CONFIG['database']

    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(conn_str)
    
    query = "SELECT * FROM students" # Assuming students table exists
    df = pd.read_sql(query, engine)
    return df