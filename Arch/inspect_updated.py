import pandas as pd
import urllib.parse
import sys

sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_excel('WP Link_Updated.xlsx')
    print("First 5 rows of WhatsApp Link:")
    for index, row in df.head().iterrows():
        link = row['WhatsApp Link']
        # Decode to verify content
        if isinstance(link, str) and 'text=' in link:
            encoded_text = link.split('text=')[1]
            decoded_text = urllib.parse.unquote(encoded_text)
            print(f"Decoded Text for {row['Customer Name']}:\n{decoded_text}")
        print("-" * 20)
except Exception as e:
    print(f"Error: {e}")
