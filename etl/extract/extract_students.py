import pandas as pd
from sqlalchemy import create_engine
from config.db_config import LMS_DB_CONFIG

def extract_student_data():
    conn_str = f"postgresql://{LMS_DB_CONFIG['user']}:{LMS_DB_CONFIG['password']}@{LMS_DB_CONFIG['host']}:{LMS_DB_CONFIG['port']}/{LMS_DB_CONFIG['database']}"
    engine = create_engine(conn_str)
    
    query = "SELECT * FROM students" # Assuming students table exists
    df = pd.read_sql(query, engine)
    return df