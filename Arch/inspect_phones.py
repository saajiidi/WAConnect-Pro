import pandas as pd

try:
    df = pd.read_excel('WP Link.xlsx')
    print("Phone (Billing) samples:")
    print(df['Phone (Billing)'].head(10))
    print("\nPhone (Billing) types:")
    print(df['Phone (Billing)'].apply(type).value_counts())
except Exception as e:
    print(f"Error: {e}")
