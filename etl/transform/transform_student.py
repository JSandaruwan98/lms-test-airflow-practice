import pandas as pd
import os

def transform_student_data(input_path): # Changed argument from 'ti' to 'input_path'
    """
    input_path: The string path passed from the DAG
    """
    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Could not find input file: {input_path}")

    # 1. Load the data
    if input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    else:
        df = pd.read_csv(input_path)

    # 2. Apply Transformations
    if 'email' in df.columns:
        df['email'] = df['email'].fillna('unknown@example.com')
    
    df['processed_at'] = pd.Timestamp.now()

    # 3. Save the transformed data
    output_path = "/tmp/transformed_students_data.parquet"
    df.to_parquet(output_path, index=False)
    
    return output_path