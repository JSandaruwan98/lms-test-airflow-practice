import pandas as pd
from sqlalchemy import text
from etl.config.db_config import WAREHOUSE_CONFIG, check_lms_warehouse_connection

def load_dim_date():
    # 1. Define the range (10 years)
    start_date = '2020-01-01'
    end_date = '2030-12-31'
    
    # 2. Generate the date range using Pandas
    df = pd.DataFrame({"full_date": pd.date_range(start_date, end_date)})
    
    # 3. Create the columns
    df['date_key'] = df['full_date'].dt.strftime('%Y%m%d').astype(int)
    df['day_name'] = df['full_date'].dt.day_name()
    df['month_name'] = df['full_date'].dt.month_name()
    df['quarter_no'] = df['full_date'].dt.quarter
    df['year_no'] = df['full_date'].dt.year
    
    # 4. Get the engine
    engine = check_lms_warehouse_connection()    
    
    # FIX 1: Convert to list of DICTIONARIES for SQLAlchemy 2.0
    # The keys in the dict must match the placeholders in the SQL below
    records = df[['date_key', 'full_date', 'day_name', 'month_name', 'quarter_no', 'year_no']].to_dict(orient='records')
    
    # FIX 2: Use named placeholders (:key_name) instead of positional (%s)
    # We wrap the string in sqlalchemy.text()
    sql = text("""
        INSERT INTO dim_date (date_key, full_date, day_name, month_name, quarter_no, year_no)
        VALUES (:date_key, :full_date, :day_name, :month_name, :quarter_no, :year_no)
        ON CONFLICT (date_key) DO NOTHING;
    """)
    
    # FIX 3: Use engine.begin() to auto-commit the transaction
    # FIX 4: Pass the entire 'records' list to execute() for bulk performance
    with engine.begin() as conn:
        conn.execute(sql, records)
            
    print(f"Successfully loaded {len(records)} days into dim_date.")

if __name__ == "__main__":
    load_dim_date()