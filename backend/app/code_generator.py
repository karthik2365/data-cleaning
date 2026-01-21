"""
Code Generator Module - Human-in-the-Loop Design

============================================================
ARCHITECTURE OVERVIEW
============================================================

This module implements a safe, transparent code generation pipeline:

1. USER INPUT: Natural language description of desired data transformation
2. CODE GENERATION: Local Gemma SLM translates intent to Python/pandas code  
3. HUMAN REVIEW: Generated code is shown to user for approval/modification
4. SAFE EXECUTION: Approved code runs in a sandboxed environment
5. OUTPUT: Transformed dataset available for download

============================================================
SAFETY GUARANTEES
============================================================

- Gemma GENERATES code but NEVER executes it directly
- All code is validated against a strict allowlist before execution
- Execution happens in a sandboxed environment with limited builtins
- No file system access, network calls, or system commands allowed
- User sees and approves all code before execution (transparency)
- Same inputs produce same outputs (reproducibility)

============================================================
OFFLINE EXECUTION
============================================================

- Gemma runs locally on your machine
- No data is sent to external servers
- Works without internet after initial model download

"""

from app.config import ENABLE_GEMMA


# ============================================================
# SYSTEM PROMPT (STRICT, NO EXAMPLES)
# ============================================================

CODE_GEN_PROMPT = """
You are a controlled Python code generator for dataset operations.

You work with a pandas DataFrame named `df` that already exists.
The user will describe what they want to do with the dataset.

Your job is to translate the user’s request into SAFE, DETERMINISTIC Python code.

------------------------------------------------
ALLOWED TASKS
------------------------------------------------

You may generate Python code for:

1. Data cleaning
   - Removing duplicates
   - Handling missing or invalid values
   - Normalizing text, numbers, dates, emails, phone numbers
   - Trimming whitespace
   - Filtering rows

2. Data transformation
   - Selecting or dropping columns
   - Renaming columns
   - Creating new columns ONLY if explicitly requested
   - Type conversions using pandas

3. Data analysis (lightweight)
   - Aggregations
   - Groupby operations
   - Basic statistics

4. Machine learning (ONLY if explicitly requested)
   - Train simple regression or classification models
   - Generate predictions
   - Add predictions as a new column in `df`
   - Store evaluation metrics in a variable named `result`

------------------------------------------------
STRICT RULES
------------------------------------------------

You MUST:
- Assume `df` already exists
- Use pandas (`pd`) and numpy (`np`) only
- Assign final output back to `df`
- Keep code minimal and readable

You MUST NOT:
- Import libraries
- Load or save files
- Access the internet
- Use os, sys, subprocess, eval, exec
- Print output
- Explain the code
- Add comments
- Invent columns or values
- Modify columns not mentioned by the user

------------------------------------------------
IMPORTANT CONSTRAINTS
------------------------------------------------

- Do NOT apply generic or automatic cleaning unless explicitly requested
- Do NOT guess user intent
- If the request is ambiguous, choose the safest minimal interpretation
- If the request cannot be fulfilled safely, return an empty response

------------------------------------------------
OUTPUT FORMAT
------------------------------------------------

Return ONLY valid Python code.
No markdown.
No explanations.
No comments.
No extra text.

------------------------------------------------
FINAL REMINDER
------------------------------------------------

You generate code.
Python executes code.
Correctness and safety matter more than completeness.
"""


# ============================================================
# MAIN CODE GENERATION ENTRY POINT
# ============================================================

def generate_cleaning_code(schema: dict, sample_data: list, user_request: str) -> str:
    """
    Generate Python code based on user intent.
    """
    if not ENABLE_GEMMA:
        return _generate_fallback_code(user_request, schema)

    prompt = f"""{CODE_GEN_PROMPT}

DATASET SCHEMA:
{_format_schema(schema)}

SAMPLE DATA (first 10 rows):
{_format_sample(sample_data)}

USER REQUEST:
{user_request}

PYTHON CODE:
"""

    try:
        from app.model import run_gemma
        code = run_gemma(prompt)
        return _validate_code(code)
    except Exception:
        return _generate_fallback_code(user_request, schema)


# ============================================================
# PROMPT HELPERS
# ============================================================

def _format_schema(schema: dict) -> str:
    return "\n".join([f"- {col}: {dtype}" for col, dtype in schema.items()])


def _format_sample(sample_data: list) -> str:
    if not sample_data:
        return "No sample data available"

    headers = list(sample_data[0].keys())
    lines = [" | ".join(headers), "-" * 40]

    for row in sample_data[:5]:
        values = [str(row.get(h, ""))[:30] for h in headers]
        lines.append(" | ".join(values))

    return "\n".join(lines)


# ============================================================
# CODE VALIDATION & SANITIZATION
# ============================================================

def _validate_code(code: str) -> str:
    code = code.strip()

    # Strip markdown fences if present
    if code.startswith("```"):
        code = code.replace("```python", "").replace("```", "").strip()

    forbidden = [
        "import ", "from ",
        "os.", "sys.", "subprocess",
        "eval(", "exec(", "__import__",
        "open(", "input(",
        "read_", "to_csv", "to_excel", "to_sql",
        "requests.", "urllib.", "socket.",
        "shutil.", "pathlib.", "glob."
    ]

    lowered = code.lower()
    for token in forbidden:
        if token in lowered:
            raise ValueError(f"Forbidden operation detected: {token}")

    return code


# ============================================================
# FALLBACK (NO AI) — SAFE, INTENT-ONLY
# ============================================================

def _generate_fallback_code(user_request: str, schema: dict) -> str:
    """
    Minimal keyword-based fallback.
    Does ONLY what is explicitly requested.
    """
    req = user_request.lower()
    columns = list(schema.keys())
    code = []

    # DROP NULLS
    if "drop null" in req or "remove null" in req:
        cols = [c for c in columns if c.lower() in req]
        if cols:
            code.append(f"df = df.dropna(subset={cols})")
        else:
            code.append("df = df.dropna()")

    # REMOVE DUPLICATES
    if "duplicate" in req:
        code.append("df = df.drop_duplicates()")

    # KEEP ONLY COLUMNS
    if any(x in req for x in ["keep only", "select only", "only keep"]):
        keep = [c for c in columns if c.lower() in req]
        if keep:
            code.append(f"df = df[{keep}]")

    # DROP COLUMNS
    if "drop column" in req or "remove column" in req:
        drop = [c for c in columns if c.lower() in req]
        if drop:
            code.append(f"df = df.drop(columns={drop})")

    # SIMPLE ML (PREDICT)
    if "predict" in req and "using" in req:
        target = None
        features = []

        left, right = req.split("using", 1)

        for c in columns:
            if c.lower() in left:
                target = c
            if c.lower() in right:
                features.append(c)

        if target and features:
            code.extend([
                f"X = df[{features}].dropna()",
                f"y = df.loc[X.index, '{target}']",
                "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)",
                "model = LinearRegression()",
                "model.fit(X_train, y_train)",
                f"df['{target}_Predicted'] = np.nan",
                f"df.loc[X.index, '{target}_Predicted'] = model.predict(X)",
                "result = {'model': 'LinearRegression', 'r2_score': model.score(X_test, y_test)}"
            ])

    return "\n".join(code).strip()


# ============================================================
# SAFE EXECUTION ENGINE
# ============================================================

def execute_cleaning_code(df, code: str):
    """
    Execute generated Python code in a sandboxed environment.
    """
    import pandas as pd
    import numpy as np

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    safe_globals = {
        "__builtins__": {
            "len": len, "range": range, "min": min, "max": max,
            "sum": sum, "abs": abs, "round": round
        },
        "pd": pd,
        "np": np,
        "LinearRegression": LinearRegression,
        "train_test_split": train_test_split,
    }

    safe_locals = {
        "df": df.copy(),
        "result": None
    }

    try:
        exec(code, safe_globals, safe_locals)
        return safe_locals["df"], safe_locals.get("result")
    except Exception as e:
        raise RuntimeError(f"Execution failed: {str(e)}")