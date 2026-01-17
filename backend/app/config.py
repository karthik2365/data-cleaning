# Gemma Data Cleaner Configuration

# ============================================================
# AI CONFIGURATION
# ============================================================
# Set to True to enable Gemma for semantic tasks (schema mapping, 
# unstructured text extraction). Set to False for pure deterministic
# cleaning with zero AI involvement.
ENABLE_GEMMA = False

# Model settings (only used when ENABLE_GEMMA = True)
MODEL_NAME = "google/gemma-3-270m"

GENERATION_CONFIG = {
    "max_new_tokens": 256,
    "do_sample": False,
    "pad_token_id": None  # Will be set from tokenizer
}

# ============================================================
# CLEANING CONFIGURATION
# ============================================================
# Maximum file size in bytes (50MB)
MAX_FILE_SIZE = 50 * 1024 * 1024

# Supported file extensions
ALLOWED_EXTENSIONS = ['.csv', '.json', '.xlsx', '.xls']

# Null value representations to clean
NULL_VALUES = [
    '', ' ', 'null', 'NULL', 'Null',
    'none', 'None', 'NONE',
    'nan', 'NaN', 'NAN',
    'n/a', 'N/A', 'NA', 'na',
    '-', '--', '---'
]