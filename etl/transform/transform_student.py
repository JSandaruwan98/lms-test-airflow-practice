import pandas as pd

def transform_student_data(df):
    # Example: Fill empty email fields with 'No Email'
    df['email'] = df['email'].fillna('unknown@example.com')
    
    # Example: Add a 'processed_at' timestamp
    df['processed_at'] = pd.to_datetime('now')
    
    return df