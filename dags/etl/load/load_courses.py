import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os
# Ensure the import matches your project structure
from etl.config.db_config import WAREHOUSE_CONFIG 

def load_course_data(file_path):
    """
    file_path: The path to the transformed course JSON data
    """
    print(f"Loading data from: {file_path}")

    # 1. Load the data from the file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")
        
    df = pd.read_json(file_path)

    # 3. Select only the columns required for the dim_course table
    # Note: 'course_key' is NOT included here because it is usually 
    # an auto-incrementing primary key handled by the database.
    final_columns = [
        'course_id',
        'course_name',
        'category',
        'duration_months'
    ]

    # Check if all columns exist, if not, fill with defaults to prevent errors
    for col in final_columns:
        if col not in df.columns:
            df[col] = None

    df_to_load = df[final_columns]

    # 4. Build the connection string
    user = WAREHOUSE_CONFIG['user']
    password = quote_plus(WAREHOUSE_CONFIG['password'])
    host = WAREHOUSE_CONFIG['host']
    port = WAREHOUSE_CONFIG['port']
    db = WAREHOUSE_CONFIG['database']

    conn_str = f"postgresql://{user}:{password}@{host}:{port}/{db}"
    engine = create_engine(conn_str)

    # 5. Load into the warehouse table 'dim_course'
    # Use 'append' to avoid the "DependentObjectsStillExist" drop error
    try:
        df_to_load.to_sql(
            'dim_course', 
            engine, 
            if_exists='append', 
            index=False, 
            method='multi'
        )
        print(f"Successfully loaded {len(df_to_load)} records to dim_course!")
    except Exception as e:
        print(f"Error loading to database: {e}")
        raise e