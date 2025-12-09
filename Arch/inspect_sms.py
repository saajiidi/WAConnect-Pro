import pandas as pd
import sys

# Set stdout to handle utf-8 if possible, or just print safely
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_excel('WP Link.xlsx')
    print("First 5 rows of Customer Name and SMS:")
    # Print row by row to avoid massive block issues
    for index, row in df.head().iterrows():
        print(f"Name: {row['Customer Name']}")
        print(f"SMS: {row['SMS']}")
        print("-" * 20)

except Exception as e:
    print(f"Error: {e}")
