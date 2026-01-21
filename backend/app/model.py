"""
Local Gemma Model Handler

This module loads and runs the Gemma Small Language Model (SLM) locally.
All inference happens on your machine - no data is sent to external servers.

Key principles:
- Offline execution: Complete privacy and no internet required after model download
- Deterministic: Same input produces same output for reproducibility
- Safe: Gemma generates code, Python validates and executes it
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.config import MODEL_NAME, GENERATION_CONFIG

# Detect available device for optimal performance
if torch.cuda.is_available():
    DEVICE = "cuda"
    DTYPE = torch.float16
    print("🚀 CUDA detected - using GPU acceleration")
elif torch.backends.mps.is_available():
    DEVICE = "mps"  # Apple Silicon
    DTYPE = torch.float16
    print("🍎 Apple Silicon detected - using MPS acceleration")
else:
    DEVICE = "cpu"
    DTYPE = torch.float32
    print("💻 Using CPU for inference")

# Load model and tokenizer once at startup
print(f"\n📦 Loading local Gemma model: {MODEL_NAME}")
print("   This runs entirely on your machine - no data leaves your computer.\n")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=DTYPE,
    device_map=DEVICE,
    low_cpu_mem_usage=True
)

# Set pad token if not set
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    
GENERATION_CONFIG["pad_token_id"] = tokenizer.pad_token_id

print(f"✅ Gemma loaded successfully on {DEVICE.upper()}!")
print("   Ready to translate your natural language requests into safe Python code.\n")


def run_gemma(prompt: str) -> str:
    """
    Run the local Gemma model to generate Python code from natural language.
    
    This function:
    1. Takes a user's natural language request (embedded in a structured prompt)
    2. Runs inference locally using Gemma
    3. Returns generated Python code for human review
    
    The generated code is NOT executed here - it's returned for validation
    and user approval first (human-in-the-loop).
    
    Args:
        prompt: Structured prompt containing system instructions, schema, and user request
        
    Returns:
        Generated Python code as a string (for human review before execution)
    """
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    
    # Move inputs to the same device as the model
    inputs = {k: v.to(DEVICE) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            **GENERATION_CONFIG
        )
    
    # Decode only the new tokens (skip the input prompt)
    generated_text = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:], 
        skip_special_tokens=True
    )
    
    return generated_text.strip()