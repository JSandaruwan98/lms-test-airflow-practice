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
def extract_task_callable():
    from etl.extract.extract_course import extract_course_data
    return extract_course_data()

def transform_task_callable(ti):
    from etl.transform.transform_courses import transform_course_data
    # 'ti' is the Task Instance, used to pull data from the previous task (XCom)
    raw_data = ti.xcom_pull(task_ids='extract_courses')
    return transform_course_data(raw_data)

# def load_task_callable(ti):
#     from etl.load.load_students import load_student_data
#     clean_data = ti.xcom_pull(task_ids='transform_students')
#     load_student_data(clean_data)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='lms_courses_etl_v2',
    default_args=default_args,
    description='ETL pipeline for LMS course data',
    schedule='@daily',
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['lms', 'course'],
) as dag:

    t1 = PythonOperator(
        task_id='extract_courses',
        python_callable=extract_task_callable
    )

    t2 = PythonOperator(
        task_id='transform_courses',
        python_callable=transform_task_callable
    )

    # t3 = PythonOperator(
    #     task_id='load_courses',
    #     python_callable=load_task_callable
    # )
    # Define dependencies
    t1 >> t2 # >> t3
