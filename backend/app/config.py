MODEL_NAME = "google/gemma-3-270m"

GENERATION_CONFIG = {
    "max_new_tokens": 256,
    "do_sample": False,
    "pad_token_id": None  # Will be set from tokenizer
}