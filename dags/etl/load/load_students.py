import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os
# Ensure the import matches your project structure
from etl.config.db_config import WAREHOUSE_CONFIG 

def load_student_data(file_path):
    """
    file_path: The path to the transformed data (passed from the DAG)
    """
    # 1. Load the data from the file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")
        
    # Since your extract task saved as CSV, we read as CSV
    df = pd.read_json(file_path)
    
    df = df.rename(columns={
        'id': 'student_id',
        'name': 'student_name',
        'created_at': 'start_date'
    })

    if 'city' not in df.columns:
        df['city'] = 'Unknown'

    df['end_date'] = None

    df['current_flag'] = 'Y'

    final_columns = [
        'student_id',
        'student_name',
        'city',
        'start_date',
        'end_date',
        'current_flag'
    ]
    df_to_load = df[final_columns]

    # 2. Build the connection string with encoded password
    user = WAREHOUSE_CONFIG['user']
    password = quote_plus(WAREHOUSE_CONFIG['password']) # Encodes '@' and other special chars
    host = WAREHOUSE_CONFIG['host']
    port = WAREHOUSE_CONFIG['port']
    db = WAREHOUSE_CONFIG['database']

    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(conn_str)

    # 3. Load into the warehouse table 'dim_students'
    df_to_load.to_sql('dim_student', engine, if_exists='append', index=False, method='multi')

    print("Data successfully loaded to dim_student!")

    
