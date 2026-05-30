import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
def extract_task_callable():
    from etl.extract.extract_payments import extract_all_lms_data
    raw_data = extract_all_lms_data()
    print(f"Extracted data saved at: {raw_data}")
    return extract_all_lms_data()
    
# def transform_task_callable(ti):
#     from etl.transform.transform_payment import transform_payment_fact
#     raw_data = ti.xcom_pull(task_ids='extract_payments')
#     return transform_payment_fact(raw_data)
    
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='lms_payments_etl_v2',
    default_args=default_args,
    description='ETL pipeline for LMS payment data',
    schedule='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['lms', 'payments'],
) as dag:
    
    t1 = PythonOperator(
        task_id='extract_payments',
        python_callable=extract_task_callable
    )
    
    t1