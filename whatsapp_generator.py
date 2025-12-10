import pandas as pd
import re
import requests
from io import BytesIO
import json
import textwrap
from urllib.parse import quote
import unicodedata
import html

class WhatsAppLinkGenerator:
    def __init__(self):
        self.phone_pattern = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4,6}')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.name_patterns = [
            re.compile(r'\b(name|full.?name|first.?name|last.?name|contact|person)\b', re.IGNORECASE),
          
        ]
        self.phone_patterns = [
            re.compile(r'\b(phone|telephone|mobile|contact|tel)\b', re.IGNORECASE),
           
        ]
        self.email_patterns = [
            re.compile(r'\b(email|e.?mail|mail)\b', re.IGNORECASE),
           
        ]

    def normalize_text(self, text):
        """Normalize text by removing extra spaces, fixing grammar, etc."""
        if not isinstance(text, str):
            return text
        
        # Remove HTML entities
        text = html.unescape(text)
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKC', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Capitalize the first letter of each sentence
        text = '. '.join([s.strip().capitalize() for s in text.split('.')])
        
        return text.strip()

    def normalize_phone(self, phone):
        """Normalize phone number to E.164 format"""
        if not isinstance(phone, str):
            phone = str(phone) if phone is not None else ""
        
        # Extract digits
        digits = re.sub(r'[^\d]', '', phone)

        # Handle Bangladesh numbers (11 digits starting with 01)
        if len(digits) == 11 and digits.startswith('01'):
            return '+88' + digits
        
        # Handle Bangladesh numbers already with 88 (13 digits starting with 8801)
        if len(digits) == 13 and digits.startswith('8801'):
            return '+' + digits

        if len(digits) == 10 and digits.startswith('1'):
            return '+880' + digits
        
        return phone

    def identify_columns(self, df):
        """Identify phone, email, and name columns in the dataframe"""
        phone_col = None
        email_col = None
        name_col = None
        
        # Check column names
        for col in df.columns:
            col_lower = str(col).lower()
            
            if phone_col is None and any(pattern.search(col_lower) for pattern in self.phone_patterns):
                phone_col = col
            elif email_col is None and any(pattern.search(col_lower) for pattern in self.email_patterns):
                email_col = col
            elif name_col is None and any(pattern.search(col_lower) for pattern in self.name_patterns):
                name_col = col
        
        # If column names don't match, check data content
        if phone_col is None or email_col is None:
            for col in df.columns:
                if phone_col is None:
                    sample_values = df[col].dropna().head(5).astype(str)
                    if any(self.phone_pattern.search(val) for val in sample_values):
                        phone_col = col
                
                if email_col is None:
                    sample_values = df[col].dropna().head(5).astype(str)
                    if any(self.email_pattern.search(val) for val in sample_values):
                        email_col = col
        
        return phone_col, email_col, name_col

    def process_file(self, file_path_or_url, is_url=False):
        """Process the input file (Excel, CSV, or Google Sheets)"""
        if is_url:
            if 'docs.google.com/spreadsheets' in file_path_or_url:
                # Google Sheets URL
                try:
                    # Extract the sheet ID from the URL
                    sheet_id = re.search(r'/d/([a-zA-Z0-9-_]+)', file_path_or_url).group(1)
                    # Export as CSV
                    export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
                    response = requests.get(export_url)
                    if response.status_code == 200:
                        df = pd.read_csv(BytesIO(response.content))
                    else:
                        raise Exception("Failed to fetch Google Sheet")
                except Exception as e:
                    raise Exception(f"Error processing Google Sheets URL: {str(e)}")
            else:
                # Other URL (assuming it's a direct file link)
                try:
                    response = requests.get(file_path_or_url)
                    if file_path_or_url.endswith('.csv'):
                        df = pd.read_csv(BytesIO(response.content))
                    else:  # Excel
                        df = pd.read_excel(BytesIO(response.content))
                except Exception as e:
                    raise Exception(f"Error downloading file from URL: {str(e)}")
        else:
            # Local file path
            try:
                if file_path_or_url.endswith('.csv'):
                    df = pd.read_csv(file_path_or_url)
                else:  # Excel
                    df = pd.read_excel(file_path_or_url)
            except Exception as e:
                raise Exception(f"Error reading local file: {str(e)}")
        
        return df

    def generate_whatsapp_links(self, df, phone_col, message):
        """Generate WhatsApp links for each phone number"""
        whatsapp_links = []
        
        for _, row in df.iterrows():
            phone = row[phone_col] if pd.notna(row[phone_col]) else ""
            if phone:
                # Normalize phone number
                normalized_phone = self.normalize_phone(str(phone))
                # Create WhatsApp link with encoded message
                encoded_message = quote(message)
                whatsapp_link = f"https://wa.me/{normalized_phone}?text={encoded_message}"
                whatsapp_links.append(whatsapp_link)
            else:
                whatsapp_links.append("")
        
        return whatsapp_links

    def process_data(self, file_path_or_url, message, is_url=False):
        """Main processing function"""
        # Process the input file
        df = self.process_file(file_path_or_url, is_url)
        
        # Normalize the message
        normalized_message = self.normalize_text(message)
        
        # Identify columns
        phone_col, email_col, name_col = self.identify_columns(df)
        
        if phone_col is None:
            raise Exception("Could not identify a phone number column in the data")
        
        # Normalize names if available
        if name_col:
            df[name_col] = df[name_col].apply(lambda x: self.normalize_text(str(x)) if pd.notna(x) else x)
        
        # Generate WhatsApp links
        whatsapp_links = self.generate_whatsapp_links(df, phone_col, normalized_message)
        
        # Add new columns to the dataframe
        df['WhatsApp Link'] = whatsapp_links
        df['WhatsApp Sent'] = "No"  # Default to "No"
        df['Email Sent'] = "No" if email_col else "N/A"  # Default to "No" or "N/A" if no email column
        
        return df, phone_col, email_col, name_col

    def save_to_excel(self, df, output_path):
        """Save the dataframe to an Excel file"""
        try:
            # Create a writer object
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # Write the dataframe to the Excel file
                df.to_excel(writer, index=False, sheet_name='WhatsApp Links')
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['WhatsApp Links']
                
                # Make the WhatsApp links clickable
                # Note: openpyxl 3.1+ might require different handling, but for 3.0.10:
                # We need to access the cells. 
                # Since we are inside the context manager, the file is saved when exiting.
                
                for row in range(2, len(df) + 2):  # +2 because of 1-indexing and header row
                    cell = worksheet.cell(row=row, column=df.columns.get_loc('WhatsApp Link') + 1)
                    if cell.value:
                        cell.hyperlink = cell.value
                        cell.style = "Hyperlink"
                
            return True
        except Exception as e:
            raise Exception(f"Error saving Excel file: {str(e)}")