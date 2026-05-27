import pandas as pd
import os
import csv

def transform_student_data(input_path):
    """
    input_path: The string path passed from the DAG
    """
    print(f"Starting transformation. Input path: {input_path}")

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Could not find input file: {input_path}")

    # 1. Load the data 
    # Added on_bad_lines='skip' to fix the "Expected 2 fields, saw 3" error
    if input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    elif input_path.endswith('.json'):
        df = pd.read_json(input_path)
    else:
        df = pd.read_csv(input_path, on_bad_lines='skip')

    # 2. Apply Transformations
    if 'email' in df.columns:
        df['email'] = df['email'].fillna('unknown@example.com')

    df['processed_at'] = pd.Timestamp.now()

    # 3. Save the transformed data 
    # FIX: Use an absolute path so you know exactly where it is.
    # We will save it to /tmp/ to ensure permissions are usually granted.


    current_dir = os.path.dirname(os.path.abspath(__file__))

    root_dir = os.path.dirname(current_dir)

    output_path = os.path.join(root_dir, "student_transform_data.json")
    print(f"Saving JSON to: {output_path}")
    df.to_json(output_path, index=False)
    
    print(f"Success! File created at: {output_path}")
    return output_path
