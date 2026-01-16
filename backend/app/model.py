import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL_NAME = "google/gemma-2b-it"

# Use CPU to avoid MPS memory issues with large attention buffers
device = "cpu"

print(f"Using device: {device}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map=None,
    torch_dtype=torch.float32,
    attn_implementation="eager",  # Avoid SDPA memory issues
    low_cpu_mem_usage=True
)

model.to(device)
model.eval()


def run_gemma(prompt: str) -> str:
    # Truncate prompt if too long to save memory
    inputs = tokenizer(
        prompt, 
        return_tensors="pt", 
        truncation=True, 
        max_length=512
    ).to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return decoded.split(prompt)[-1].strip()