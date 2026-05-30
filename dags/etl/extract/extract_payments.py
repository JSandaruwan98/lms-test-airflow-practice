import pandas as pd
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from etl.config.db_config import check_lms_db_connection, check_lms_warehouse_connection
import csv
import os

def extract_latest_payments_data(engine, warehouse_engine):
    try:
        with warehouse_engine.connect() as conn:
            result = conn.execute(text("SELECT MAX(payment_id) FROM dim_payments"))
            last_id = result.scalar()
            
            if last_id is None:
                last_id = 0
                
        print(f"Last payment_id found in Warehouse: {last_id}")
        
    except Exception as e:
        print(f"Could not check last ID (maybe table doesn't exist yet): {e}")
        last_id = 0

    query = f"SELECT * FROM payments WHERE id > {last_id}"
    
    print(f"Fetching new records from source where id > {last_id}...")
    df = pd.read_sql(query, engine)

    if df.empty:
        print("No new records to fetch.")
    else:
        print(f"Extracted {len(df)} new records.")

    return df

def extract_all_lms_data():
    # 1. Setup Connections
    engine = check_lms_db_connection()
    warehouse_engine = check_lms_warehouse_connection()
    
    # 2. Setup Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir) 
    
    # Dictionary to keep track of file paths
    extracted_paths = {}

    print("--- Starting Full Extraction Process ---")

    # --- Part 1: Extract Dimensions ---
    tables_to_extract = [
        ("dim_student", "dim_student.json"),
        ("dim_course", "dim_course.json"),
        ("dim_institute", "dim_institute.json"),
        ("dim_date", "dim_date.json")
    ]
    
    for table_name, file_name in tables_to_extract:
        try:
            query = f"SELECT * FROM {table_name}"
            df_dim = pd.read_sql(query, warehouse_engine)
            
            json_path = os.path.join(root_dir, file_name)
            df_dim.to_json(json_path, orient='records', indent=4, date_format='iso')
            
            # Store the path in our dictionary
            extracted_paths[table_name] = json_path
            print(f"Successfully saved {table_name} to {json_path}")
        except Exception as e:
            print(f"Error extracting {table_name}: {e}")
            extracted_paths[table_name] = None

    # --- Part 2: Extract Payment Data ---
    try:
        df_payments = extract_latest_payments_data(engine, warehouse_engine)
        payment_json_path = os.path.join(root_dir, "payments_extract_data.json")
        
        df_payments.to_json(payment_json_path, orient='records', indent=4)
        extracted_paths['payments'] = payment_json_path
        print(f"Successfully saved payment data to: {payment_json_path}")
    except Exception as e:
        print(f"Error extracting payment data: {e}")
        extracted_paths['payments'] = None

    print("--- All Extractions Complete ---")

    # Return the specific paths requested
    return (
        extracted_paths.get('payments'),
        extracted_paths.get('dim_student'),
        extracted_paths.get('dim_course'),
        extracted_paths.get('dim_institute')
    )