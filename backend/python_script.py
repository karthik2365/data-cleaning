"""
Deterministic Data Cleaning Script
No AI/LLM - Pure rule-based cleaning to avoid hallucinations
"""

import pandas as pd
import re
import json
from datetime import datetime
from typing import Union, List, Dict, Any
import argparse
import sys


class DataCleaner:
    """Rule-based data cleaner with deterministic transformations"""
    
    def __init__(self):
        self.cleaning_stats = {
            "rows_processed": 0,
            "nulls_removed": 0,
            "duplicates_removed": 0,
            "values_standardized": 0,
            "dates_fixed": 0,
            "emails_fixed": 0,
            "phones_fixed": 0,
            "whitespace_trimmed": 0
        }
    
    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Main cleaning pipeline for DataFrames"""
        self.cleaning_stats["rows_processed"] = len(df)
        
        # 1. Remove completely empty rows
        df = df.dropna(how='all')
        
        # 2. Remove duplicate rows
        initial_len = len(df)
        df = df.drop_duplicates()
        self.cleaning_stats["duplicates_removed"] = initial_len - len(df)
        
        # 3. Clean each column based on detected type
        for col in df.columns:
            df[col] = self._clean_column(df[col], col)
        
        return df
    
    def _clean_column(self, series: pd.Series, col_name: str) -> pd.Series:
        """Clean a single column based on its content type"""
        # Detect column type and apply appropriate cleaning
        col_lower = col_name.lower()
        
        if any(x in col_lower for x in ['email', 'mail', 'e-mail']):
            return series.apply(self._clean_email)
        elif any(x in col_lower for x in ['phone', 'tel', 'mobile', 'cell']):
            return series.apply(self._clean_phone)
        elif any(x in col_lower for x in ['date', 'time', 'dob', 'birth', 'created', 'updated']):
            return series.apply(self._clean_date)
        elif any(x in col_lower for x in ['name', 'first', 'last', 'full']):
            return series.apply(self._clean_name)
        elif any(x in col_lower for x in ['address', 'street', 'city', 'state', 'country', 'zip', 'postal']):
            return series.apply(self._clean_address)
        elif any(x in col_lower for x in ['price', 'amount', 'cost', 'salary', 'revenue', 'total']):
            return series.apply(self._clean_numeric)
        else:
            return series.apply(self._clean_generic)
    
    def _clean_email(self, value: Any) -> Any:
        """Clean and validate email addresses"""
        if pd.isna(value) or value == '':
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        value = str(value).strip().lower()
        
        # Remove common typos and extra characters
        value = re.sub(r'\s+', '', value)  # Remove spaces
        value = value.replace('..', '.').replace('@@', '@')
        
        # Basic email pattern validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, value):
            self.cleaning_stats["emails_fixed"] += 1
            return value
        
        return value if '@' in value else None
    
    def _clean_phone(self, value: Any) -> Any:
        """Standardize phone numbers"""
        if pd.isna(value) or value == '':
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        # Extract only digits
        digits = re.sub(r'\D', '', str(value))
        
        if len(digits) == 0:
            return None
        
        # Format based on length (assuming US format for 10 digits)
        if len(digits) == 10:
            formatted = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            self.cleaning_stats["phones_fixed"] += 1
            return formatted
        elif len(digits) == 11 and digits[0] == '1':
            formatted = f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
            self.cleaning_stats["phones_fixed"] += 1
            return formatted
        
        return digits  # Return cleaned digits if format unknown
    
    def _clean_date(self, value: Any) -> Any:
        """Parse and standardize dates to ISO format"""
        if pd.isna(value) or value == '':
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        value = str(value).strip()
        
        # Common date formats to try
        date_formats = [
            '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%Y.%m.%d', '%d.%m.%Y', '%m.%d.%Y',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y',
            '%Y%m%d', '%d%m%Y',
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(value, fmt)
                self.cleaning_stats["dates_fixed"] += 1
                return parsed.strftime('%Y-%m-%d')  # ISO format
            except ValueError:
                continue
        
        return value  # Return original if can't parse
    
    def _clean_name(self, value: Any) -> Any:
        """Clean and standardize names"""
        if pd.isna(value) or value == '':
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        value = str(value).strip()
        
        # Remove extra whitespace
        value = ' '.join(value.split())
        
        # Title case (capitalize first letter of each word)
        value = value.title()
        
        # Fix common issues
        value = re.sub(r'[^\w\s\'-]', '', value)  # Keep only letters, spaces, hyphens, apostrophes
        
        self.cleaning_stats["values_standardized"] += 1
        return value
    
    def _clean_address(self, value: Any) -> Any:
        """Clean and standardize addresses"""
        if pd.isna(value) or value == '':
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        value = str(value).strip()
        
        # Remove extra whitespace
        value = ' '.join(value.split())
        
        # Standardize common abbreviations
        replacements = {
            r'\bst\b': 'Street',
            r'\bave\b': 'Avenue',
            r'\bblvd\b': 'Boulevard',
            r'\brd\b': 'Road',
            r'\bdr\b': 'Drive',
            r'\bln\b': 'Lane',
            r'\bapt\b': 'Apartment',
            r'\bste\b': 'Suite',
        }
        
        for pattern, replacement in replacements.items():
            value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
        
        self.cleaning_stats["values_standardized"] += 1
        return value.title()
    
    def _clean_numeric(self, value: Any) -> Any:
        """Clean numeric/currency values"""
        if pd.isna(value) or value == '':
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        value = str(value).strip()
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[$€£¥,]', '', value)
        
        try:
            # Try to convert to float
            num = float(cleaned)
            self.cleaning_stats["values_standardized"] += 1
            return round(num, 2)
        except ValueError:
            return value
    
    def _clean_generic(self, value: Any) -> Any:
        """Generic cleaning for untyped columns"""
        if pd.isna(value):
            self.cleaning_stats["nulls_removed"] += 1
            return None
        
        if isinstance(value, str):
            # Trim whitespace
            cleaned = value.strip()
            if cleaned != value:
                self.cleaning_stats["whitespace_trimmed"] += 1
            
            # Remove extra internal whitespace
            cleaned = ' '.join(cleaned.split())
            
            # Return None for empty strings
            if cleaned == '':
                self.cleaning_stats["nulls_removed"] += 1
                return None
            
            return cleaned
        
        return value
    
    def clean_json(self, data: Union[Dict, List]) -> Union[Dict, List]:
        """Clean JSON/dict data"""
        if isinstance(data, list):
            return [self._clean_dict(item) if isinstance(item, dict) else item for item in data]
        elif isinstance(data, dict):
            return self._clean_dict(data)
        return data
    
    def _clean_dict(self, d: Dict) -> Dict:
        """Clean a single dictionary"""
        cleaned = {}
        for key, value in d.items():
            # Clean the key
            clean_key = str(key).strip().lower().replace(' ', '_')
            
            # Clean the value based on key hints
            if value is None or value == '' or value == 'null' or value == 'NULL':
                continue  # Skip null/empty values
            
            if isinstance(value, str):
                value = value.strip()
                if value == '':
                    continue
            
            cleaned[clean_key] = value
        
        self.cleaning_stats["rows_processed"] += 1
        return cleaned
    
    def get_stats(self) -> Dict:
        """Return cleaning statistics"""
        return self.cleaning_stats


def clean_csv(input_path: str, output_path: str = None) -> pd.DataFrame:
    """Clean a CSV file"""
    cleaner = DataCleaner()
    
    # Read CSV
    df = pd.read_csv(input_path)
    print(f"📖 Loaded {len(df)} rows from {input_path}")
    
    # Clean
    cleaned_df = cleaner.clean_dataframe(df)
    print(f"🧹 Cleaned data: {len(cleaned_df)} rows remaining")
    
    # Save if output path provided
    if output_path:
        cleaned_df.to_csv(output_path, index=False)
        print(f"💾 Saved to {output_path}")
    
    # Print stats
    stats = cleaner.get_stats()
    print("\n Cleaning Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return cleaned_df


def clean_json_file(input_path: str, output_path: str = None) -> Union[Dict, List]:
    """Clean a JSON file"""
    cleaner = DataCleaner()
    
    # Read JSON
    with open(input_path, 'r') as f:
        data = json.load(f)
    print(f"📖 Loaded data from {input_path}")
    
    # Clean
    cleaned_data = cleaner.clean_json(data)
    print("Data cleaned successfully")
    
    # Save if output path provided
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(cleaned_data, f, indent=2)
        print(f"💾 Saved to {output_path}")
    
    # Print stats
    stats = cleaner.get_stats()
    print("\n Cleaning Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    return cleaned_data


def main():
    parser = argparse.ArgumentParser(description='Deterministic Data Cleaner - No AI, No Hallucinations')
    parser.add_argument('input', help='Input file path (CSV or JSON)')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    parser.add_argument('-f', '--format', choices=['csv', 'json'], help='Force input format')
    
    args = parser.parse_args()
    
    # Detect format
    input_lower = args.input.lower()
    if args.format:
        file_format = args.format
    elif input_lower.endswith('.csv'):
        file_format = 'csv'
    elif input_lower.endswith('.json'):
        file_format = 'json'
    else:
        print("❌ Could not detect file format. Use --format to specify.")
        sys.exit(1)
    
    # Generate output path if not provided
    output_path = args.output
    if not output_path:
        base = args.input.rsplit('.', 1)[0]
        output_path = f"{base}_cleaned.{file_format}"
    
    print("🧹 Deterministic Data Cleaner")
    print("   No AI • No Hallucinations • Pure Rules")
    print("=" * 50)
    
    # Clean based on format
    if file_format == 'csv':
        clean_csv(args.input, output_path)
    else:
        clean_json_file(args.input, output_path)
    
    print("\n Done!")


if __name__ == '__main__':
    main()
