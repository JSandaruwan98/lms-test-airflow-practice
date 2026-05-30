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

def extract_dimensions_to_json():
    warehouse_engine = check_lms_warehouse_connection()
        
    tables_to_extract = [
        ("dim_student", "dim_student.json"),
        ("dim_course", "dim_course.json"),
        ("dim_institute", "dim_institute.json"),
        ("dim_date", "dim_date.json")
    ]
    
    print("--- Starting Dimension Extraction ---")
    
    for table_name, file_name in tables_to_extract:
        try:
            # Technical Step: Read from SQL
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, warehouse_engine)
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            root_dir = os.path.dirname(current_dir) 
            
            json_path = os.path.join(root_dir, file_name)
            df.to_json(json_path, orient='records', indent=4, date_format='iso')
            
            print(f"Successfully saved {table_name} to {json_path}")

        except Exception as e:
            print(f"Error extracting {table_name}: {e}")

    print("--- All Dimensions Extracted ---")
    return root_dir


def extract_payment_data():
    engine = check_lms_db_connection()
    warehouse_engine = check_lms_warehouse_connection()
    
    df = extract_latest_payments_data(engine, warehouse_engine)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    root_dir = os.path.dirname(current_dir) 
    
    json_path = os.path.join(root_dir, "payments_extract_data.json")
    print(f"Saving JSON to: {json_path}")
    df.to_json(json_path, orient='records', indent=4)

    print("Success! Check your folder now.")

    return json_path