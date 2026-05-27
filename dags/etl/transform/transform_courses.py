import pandas as pd
import os

def transform_course_data(input_path):
    """
    input_path: The path to the extracted course data (JSON/Parquet/CSV)
    """
    print(f"Starting Course transformation. Input path: {input_path}")

    if not input_path or not os.path.exists(input_path):
        raise FileNotFoundError(f"Could not find input file: {input_path}")

    # 1. Load the data 
    if input_path.endswith('.parquet'):
        df = pd.read_parquet(input_path)
    elif input_path.endswith('.json'):
        df = pd.read_json(input_path)
    else:
        df = pd.read_csv(input_path, on_bad_lines='skip')

    # 2. Apply Course-Specific Transformations
    
    # Rename columns to match a Warehouse standard (optional but recommended)
    # This maps 'id' to 'course_id' and 'name' to 'course_name'
    df = df.rename(columns={
        'id': 'course_id',
        'name': 'course_name'
    })

    # Data Cleaning: Ensure price is not null
    if 'price' in df.columns:
        df['price'] = df['price'].fillna(0.0)

    # Add metadata for the ETL process
    df['processed_at'] = pd.Timestamp.now()
    
    # Add a 'current_flag' like we did for students (if your dim_course uses it)
    df['current_flag'] = 'Y' 

    # 3. Save the transformed data 
    # Logic to find the root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(current_dir) # Goes up one level to root

    output_path = os.path.join(root_dir, "course_transform_data.json")
    
    print(f"Saving transformed data to: {output_path}")
    
    # FIX: orient='records' makes it look like your input JSON 
    # indent=4 makes it readable
    df.to_json(output_path, orient='records', indent=4, date_format='iso')
    
    print(f"Success! File created at: {output_path}")
    return output_path