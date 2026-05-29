from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import sys
import os

# Adjust path to find your ETL scripts
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def load_date_task():
    from etl.load.load_date import load_dim_date
    load_dim_date()

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='lms_dim_date_loader',
    default_args=default_args,
    description='Populates the static Date Dimension',
    schedule_interval='@once',  # You only need to run this once
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['lms', 'dates'],
) as dag:

    t1 = PythonOperator(
        task_id='populate_dim_date',
        python_callable=load_date_task
    )

    t1