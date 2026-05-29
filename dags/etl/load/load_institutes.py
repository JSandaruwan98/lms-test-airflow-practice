import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus
import os
# Ensure the import matches your project structure
from etl.config.db_config import WAREHOUSE_CONFIG, check_lms_warehouse_connection

def load_institute_data(file_path):
    """
    file_path: The path to the transformed data (passed from the DAG)
    """
    # 1. Load the data from the file path
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} was not found.")
        
    # Since your extract task saved as CSV, we read as CSV
    df = pd.read_json(file_path)

    if 'city' not in df.columns:
        df['city'] = 'Unknown'

    df['end_date'] = None

    df['current_flag'] = 'Y'

    final_columns = [
        'institute_id',
        'institute_name',
        'city',
        'start_date',
        'end_date',
        'current_flag'
    ]
    df_to_load = df[final_columns]
    
    engine = check_lms_warehouse_connection()

    # 3. Load into the warehouse table 'dim_institutes'
    df_to_load.to_sql('dim_institute', engine, if_exists='append', index=False, method='multi')

    print("Data successfully loaded to dim_institute!")

    
