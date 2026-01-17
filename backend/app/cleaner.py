"""Deterministic Data Cleaner - No AI, No Hallucinations"""
import re
from datetime import datetime
from typing import Any


class RecordCleaner:
    """Rule-based record cleaner with deterministic transformations"""
    
    def __init__(self):
        self.stats = {"cleaned": 0}
    
    def clean_record(self, record: dict) -> dict:
        """Clean a single record/row"""
        if not record:
            return None
        
        cleaned = {}
        for key, value in record.items():
            # Clean the key
            clean_key = str(key).strip()
            
            # Clean the value based on key hints
            cleaned_value = self._clean_value(value, clean_key)
            
            # Only include non-null values
            if cleaned_value is not None:
                cleaned[clean_key] = cleaned_value
        
        self.stats["cleaned"] += 1
        return cleaned if cleaned else None
    
    def _clean_value(self, value: Any, key: str) -> Any:
        """Clean a value based on its content and key hint"""
        # Handle null/empty
        if value is None or value == '' or str(value).strip() == '':
            return None
        if str(value).lower() in ('null', 'none', 'nan', 'n/a', 'na', '-'):
            return None
        
        # Convert to string for processing
        if isinstance(value, (int, float)):
            return value  # Keep numbers as-is
        
        value = str(value).strip()
        key_lower = key.lower()

        # Apply type-specific cleaning based on column name
        if any(x in key_lower for x in ['email', 'mail', 'e-mail']):
            return self._clean_email(value)
        elif any(x in key_lower for x in ['phone', 'tel', 'mobile', 'cell']):
            return self._clean_phone(value)
        elif any(x in key_lower for x in ['date', 'time', 'dob', 'birth', 'created', 'updated']):
            return self._clean_date(value)
        elif any(x in key_lower for x in ['name', 'first', 'last']):
            return self._clean_name(value)
        elif any(x in key_lower for x in ['price', 'amount', 'cost', 'salary', 'revenue', 'total']):
            return self._clean_currency(value)
        else:
            return self._clean_generic(value)
    
    def _clean_email(self, value: str) -> str:
        """Clean email addresses"""
        value = value.lower().strip()
        value = re.sub(r'\s+', '', value)
        value = value.replace('..', '.').replace('@@', '@')
        return value if '@' in value and '.' in value else None
    
    def _clean_phone(self, value: str) -> str:
        """Standardize phone numbers"""
        digits = re.sub(r'\D', '', value)
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        return digits if digits else None
    
    def _clean_date(self, value: str) -> str:
        """Parse and standardize dates to ISO format"""
        date_formats = [
            '%Y-%m-%d', '%d-%m-%Y', '%m-%d-%Y',
            '%Y/%m/%d', '%d/%m/%Y', '%m/%d/%Y',
            '%B %d, %Y', '%b %d, %Y', '%d %B %Y',
        ]
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return value
    
    def _clean_name(self, value: str) -> str:
        """Clean and standardize names"""
        value = ' '.join(value.split())  # Remove extra whitespace
        value = re.sub(r'[^\w\s\'-]', '', value)  # Keep only valid chars
        return value.title()
    
    def _clean_currency(self, value: str) -> Any:
        """Clean currency/numeric values"""
        cleaned = re.sub(r'[$€£¥,]', '', value)
        try:
            return round(float(cleaned), 2)
        except ValueError:
            return value
    
    def _clean_generic(self, value: str) -> str:
        """Generic string cleaning"""
        return ' '.join(value.split())  # Trim and normalize whitespace


# Global cleaner instance
_cleaner = RecordCleaner()


def clean_record(record: dict) -> dict:
    """Clean a single record using deterministic rules (no AI)"""
    return _cleaner.clean_record(record)