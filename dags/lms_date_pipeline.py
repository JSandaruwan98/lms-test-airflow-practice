import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Project root fix (keep this if your modules aren't in /dags or /plugins)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Standard ETL functions using Task dependencies
def load_date_task():
    from etl.load.load_date import load_dim_date
    load_dim_date()
    
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='lms_date_pipeline_v2',
    default_args=default_args,
    description='ETL pipeline for LMS date data',
    schedule='@once',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['lms', 'date_static'],
) as dag:
    
    t1 = PythonOperator(
        task_id='populate_dim_date',
        python_callable=load_date_task
    )
    
    # Define dependencies
    t1 
