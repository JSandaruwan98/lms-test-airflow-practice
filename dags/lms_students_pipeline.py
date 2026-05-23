import sys
import os
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# --- ADD THESE 2 LINES ---
# This allows Airflow to find the 'etl' and 'config' folders
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Now your imports will work
from etl.extract.extract_students import extract_student_data
from etl.transform.transform_students import transform_student_data
from etl.load.load_students import load_student_data

def run_etl_process():
    raw_data = extract_student_data()
    clean_data = transform_student_data(raw_data)
    load_student_data(clean_data)

with DAG(
    dag_id='lms_students_etl',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    etl_task = PythonOperator(
        task_id='run_students_etl',
        python_callable=run_etl_process
    )