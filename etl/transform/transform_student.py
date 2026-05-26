import pandas as pd
import os

def transform_students(ti):
    """
    ti: The Airflow Task Instance object (used to pull data from XCom)
    """
    # 1. Get the file path from the 'extract_task'
    # 'extract_task' must match the task_id defined in your DAG
    input_path = ti.xcom_pull(task_ids='extract_task')
    
    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Could not find input file: {input_path}")

    # 2. Load the data (using read_parquet or read_csv based on your extract task)
    if input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    # 3. Apply Transformations
    # Fill empty email fields
    if 'email' in df.columns:
        df['email'] = df['email'].fillna('unknown@example.com')
    
    # Add a 'processed_at' timestamp
    # Note: pd.Timestamp.now() is the modern way to get 'now' in Pandas
    df['processed_at'] = pd.Timestamp.now()

    # 4. Save the transformed data to a new file
    output_path = "/tmp/transformed_students_data.parquet"
    df.to_parquet(output_path, index=False)
    
    print(f"Transformation complete. File saved to {output_path}")

    # 5. Return the path so the LOAD task can find it
    return output_path