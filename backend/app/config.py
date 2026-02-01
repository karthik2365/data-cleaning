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
# Enable LLM for natural language to code translation.
# When True: Uses local LLM model to interpret user requests
# When False: Falls back to keyword-based code generation
ENABLE_LLM = True

# ============================================================
# MODEL SETTINGS - CHANGE MODEL NAME HERE
# ============================================================
# To change the model, simply update MODEL_NAME below.
# Available Ollama models: llama3.2, llama3.2:1b, llama3.2:3b, 
#                          codellama, mistral, etc.
# Run 'ollama list' to see installed models
# Run 'ollama pull <model_name>' to download new models
MODEL_NAME = "llama3.2"  # <-- CHANGE MODEL HERE

# Ollama API endpoint (change if running Ollama on different host/port)
OLLAMA_BASE_URL = "http://localhost:11434"

# Generation settings for Ollama
GENERATION_CONFIG = {
    "temperature": 0.1,          # Low temperature for consistent code
    "num_predict": 512,          # Max tokens to generate
    "top_p": 0.9,                # Nucleus sampling
    "stop": ["```", "\n\n\n"]    # Stop sequences
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