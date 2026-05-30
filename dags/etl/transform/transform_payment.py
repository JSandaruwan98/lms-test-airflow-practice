import pandas as pd
import os

def transform_payment_fact(payment_json_path, dim_student_path, dim_course_path, dim_institute_path):
    print("--- Starting Payment Fact Transformation ---")

    # 1. LOAD RAW DATA
    # This is your extracted JSON with student_id, course_id, etc.
    if not os.path.exists(payment_json_path):
        raise FileNotFoundError(f"Input file not found: {payment_json_path}")
    
    df_raw = pd.read_json(payment_json_path)

    # 2. LOAD DIMENSIONS (The Lookup Tables)
    # We load these to get the Surrogate Keys (the 'key' columns)
    dim_student = pd.read_json(dim_student_path)
    dim_course = pd.read_json(dim_course_path)
    dim_institute = pd.read_json(dim_institute_path)

    # 3. TECHNICAL STEP: TRANSFORM DATE
    # Your date is in Milliseconds (1777593600000). We need to make it an Integer (YYYYMMDD)
    # Convert Unix MS to datetime objects
    df_raw['payment_date_dt'] = pd.to_datetime(df_raw['payment_date'], unit='ms')
    
    # Create the date_key (e.g., 20260530) to match your dim_date keys
    df_raw['date_key'] = df_raw['payment_date_dt'].dt.strftime('%Y%m%d').astype(int)

    # 4. TECHNICAL STEP: SURROGATE KEY LOOKUPS (The "Join")
    # We join the raw student_id to the dimension's student_id to find the student_key
    
    # Student Lookup
    df_fact = pd.merge(
        df_raw, 
        dim_student[['student_key', 'student_id']], 
        on='student_id', 
        how='left'
    )

    # Course Lookup
    df_fact = pd.merge(
        df_fact, 
        dim_course[['course_key', 'course_id']], 
        on='course_id', 
        how='left'
    )

    # Institute Lookup
    df_fact = pd.merge(
        df_fact, 
        dim_institute[['institute_key', 'institute_id']], 
        on='institute_id', 
        how='left'
    )

    # 5. DATA CLEANING: Handle Missing Keys (The -1 Rule)
    # If a join fails (e.g., student not found), fill with -1
    df_fact['student_key'] = df_fact['student_key'].fillna(-1).astype(int)
    df_fact['course_key'] = df_fact['course_key'].fillna(-1).astype(int)
    df_fact['institute_key'] = df_fact['institute_key'].fillna(-1).astype(int)

    # 6. SELECT FINAL COLUMNS
    # A Fact table should only contain Keys and Measures
    final_cols = [
        'student_key', 
        'course_key', 
        'institute_key', 
        'date_key', 
        'amount', 
        'payment_method',
        'id' # Keeping source ID for auditing
    ]
    df_final = df_fact[final_cols].rename(columns={'id': 'source_payment_id'})

    # 7. SAVE TO JSON
    output_path = os.path.join(os.getcwd(), "fact_payment_transformed.json")
    df_final.to_json(output_path, orient='records', indent=4)
    
    print(f"Success! Fact table data saved to: {output_path}")
    return df_final

# --- HOW TO RUN IT ---
# (Update these paths to where your JSON files are saved)
# transform_payment_fact(
#     'payment_extract.json', 
#     'dim_student.json', 
#     'dim_course.json', 
#     'dim_institute.json'
# )