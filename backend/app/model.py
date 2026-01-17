from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from app.config import MODEL_NAME, GENERATION_CONFIG

# Load model and tokenizer once at startup
print(f"Loading model: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32,  # Use float32 for CPU
    device_map="cpu"
)

# Set pad token if not set
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
    
GENERATION_CONFIG["pad_token_id"] = tokenizer.pad_token_id

print("Model loaded successfully!")


def run_gemma(prompt: str) -> str:
    """Run the Gemma model with the given prompt and return the generated text."""
    inputs = tokenizer(prompt, return_tensors="pt", padding=True)
    
    with torch.no_grad():
        outputs = model.generate(
            inputs.input_ids,
            attention_mask=inputs.attention_mask,
            **GENERATION_CONFIG
        )
    
    # Decode only the new tokens (skip the input)
    generated_text = tokenizer.decode(
        outputs[0][inputs.input_ids.shape[1]:], 
        skip_special_tokens=True
    )
    
    return generated_text.strip()
