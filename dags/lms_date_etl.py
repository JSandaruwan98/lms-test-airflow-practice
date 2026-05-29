import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Adjust path to find your ETL scripts
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def extract_task_callable():
    from etl.extract.extract_course import extract_course_data
    return extract_course_data()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='lms_date_v2',
    default_args=default_args,
    description='Populates the static Date Dimension',
    schedule='@daily',  # You only need to run this once
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['lms', 'date'],
) as dag:
    
    t1 = PythonOperator(
        task_id='extract_courses',
        python_callable=extract_task_callable
    )

    t1