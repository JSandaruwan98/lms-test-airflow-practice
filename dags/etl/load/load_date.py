import pandas as pd
from etl.config.db_config import WAREHOUSE_CONFIG, check_lms_warehouse_connection

def load_dim_date():
    # 1. Define the range (10 years)
    start_date = '2020-01-01'
    end_date = '2030-12-31'
    
    # 2. Generate the date range using Pandas
    df = pd.DataFrame({"full_date": pd.date_range(start_date, end_date)})
    
    # 3. Create the columns to match your \d dim_date output
    df['date_key'] = df['full_date'].dt.strftime('%Y%m%d').astype(int)
    df['day_name'] = df['full_date'].dt.day_name()
    df['month_name'] = df['full_date'].dt.month_name()
    df['quarter_no'] = df['full_date'].dt.quarter
    df['year_no'] = df['full_date'].dt.year
    
    # 4. Use PostgresHook to load it
    engine = check_lms_warehouse_connection()    
    
    # Convert to list of tuples for insertion
    records = df[['date_key', 'full_date', 'day_name', 'month_name', 'quarter_no', 'year_no']].values.tolist()
    
    # Upsert logic (Insert, or skip if the date_key already exists)
    sql = """
    INSERT INTO dim_date (date_key, full_date, day_name, month_name, quarter_no, year_no)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (date_key) DO NOTHING;
    """
    
    with engine.connect() as conn:
        for record in records:
            conn.execute(sql, record)
            
    print(f"Successfully loaded {len(records)} days into dim_date.")