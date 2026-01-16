import json
import re
from app.model import run_gemma


SYSTEM_PROMPT = """You are a data-cleaning engine.
Rules:
- Output ONLY valid JSON object
- Clean and normalize the data (fix typos, standardize formats)
- Remove empty/null values
- Do NOT add explanations
- Return a single JSON object with cleaned key-value pairs"""


def clean_record(record: dict):
    prompt = f"""{SYSTEM_PROMPT}

Input data:
{json.dumps(record, indent=2)}

Return cleaned JSON:"""

    raw_output = run_gemma(prompt)
    
    # Try to extract JSON from the output
    try:
        # First try direct parsing
        parsed = json.loads(raw_output)
        return parsed
    except json.JSONDecodeError:
        # Try to find JSON object in the output
        json_match = re.search(r'\{[^{}]*\}', raw_output, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return parsed
            except json.JSONDecodeError:
                pass
        
        # If all else fails, return the original record cleaned
        return {k: v for k, v in record.items() if v is not None and v != ""}