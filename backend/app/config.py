# Gemma Data Cleaner Configuration
# ============================================================
# Local AI-Assisted Data Processing
# ============================================================
# This application uses a Small Language Model (Gemma) running LOCALLY
# to generate safe Python (pandas) code based on user's natural language
# requests. All processing happens offline - no data leaves your machine.
#
# Human-in-the-loop design:
# - Gemma generates code, but never executes it directly
# - Users review and approve generated code before execution
# - Full transparency and reproducibility
# ============================================================

# ============================================================
# AI CONFIGURATION
# ============================================================
# Enable Gemma for natural language to code translation.
# When True: Uses local Gemma model to interpret user requests
# When False: Falls back to keyword-based code generation
ENABLE_GEMMA = True

# Model settings - Gemma runs locally for privacy and offline use
MODEL_NAME = "google/gemma3:1b"  # Instruction-tuned Gemma 2 for better code generation

GENERATION_CONFIG = {
    "max_new_tokens": 512,       # Allow longer code generation
    "do_sample": False,          # Deterministic output for reproducibility
    "temperature": 0.1,          # Low temperature for consistent code
    "pad_token_id": None         # Will be set from tokenizer
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