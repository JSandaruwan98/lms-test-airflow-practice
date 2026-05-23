from sqlalchemy import create_engine
from config.db_config import WAREHOUSE_CONFIG

def load_student_data(df):
    conn_str = f"postgresql://{WAREHOUSE_CONFIG['user']}:{WAREHOUSE_CONFIG['password']}@{WAREHOUSE_CONFIG['host']}:{WAREHOUSE_CONFIG['port']}/{WAREHOUSE_CONFIG['database']}"
    engine = create_engine(conn_str)
    
    # Load into a table called 'dim_students' in the warehouse
    df.to_sql('dim_students', engine, if_exists='replace', index=False)
    print("Data successfully loaded to Warehouse!")