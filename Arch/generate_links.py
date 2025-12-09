import pandas as pd
import urllib.parse

def clean_phone(phone):
    # Convert to string, remove non-digits
    phone_str = str(phone)
    cleaned = ''.join(filter(str.isdigit, phone_str))
    
    # Logic to add country code 880
    if cleaned.startswith('88'):
        return cleaned
    elif cleaned.startswith('01'):
        return '88' + cleaned
    elif cleaned.startswith('1') and len(cleaned) == 10:
        return '880' + cleaned
    
    return cleaned

def generate_link(row):
    phone = row['Phone (Billing)']
    sms = row['SMS']
    name = row['Customer Name']
    
    if pd.isna(phone) or pd.isna(sms):
        return ""
    
    cleaned_phone = clean_phone(phone)
    
    customer_name = str(name) if not pd.isna(name) else ""
    
    full_message = f"Assalamu Alikum, {customer_name} Sir!\n\n{sms}"
    
    encoded_sms = urllib.parse.quote(full_message)
    return f"https://wa.me/{cleaned_phone}?text={encoded_sms}"

try:
    # Read the excel file
    file_path = 'WP Link.xlsx'
    df = pd.read_excel(file_path)
    
    # Generate links
    df['WhatsApp Link'] = df.apply(generate_link, axis=1)
    
    # Save to a new file to avoid permission issues
    new_file_path = 'WP Link_Updated.xlsx'
    df.to_excel(new_file_path, index=False)
    print(f"Successfully generated WhatsApp links and saved to {new_file_path}")
    
except Exception as e:
    print(f"An error occurred: {e}")
