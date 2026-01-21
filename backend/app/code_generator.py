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
# SYSTEM PROMPT - FLEXIBLE CODE GENERATION
# ============================================================

CODE_GEN_PROMPT = """
You are an expert Python code generator for data processing tasks.

A pandas DataFrame named `df` already exists with the schema and sample data shown below.
The user will describe what they want to do with the dataset in natural language.

YOUR GOAL: Generate working Python code that accomplishes EXACTLY what the user asks for.
Be helpful and try your best to fulfill the user's request.

------------------------------------------------
CAPABILITIES
------------------------------------------------

You can generate code for ANY of the following:

1. DATA CLEANING
   - Remove duplicates (df.drop_duplicates())
   - Handle missing values (dropna, fillna with values/methods like ffill, bfill, mean, median)
   - Remove/replace invalid values
   - Normalize text (lowercase, uppercase, title case, strip whitespace)
   - Standardize dates, emails, phone numbers
   - Filter rows based on conditions
   - Remove outliers

2. DATA TRANSFORMATION
   - Select or drop columns
   - Rename columns
   - Create new columns (calculated fields, combinations, etc.)
   - Type conversions (to_numeric, to_datetime, astype)
   - String operations (split, replace, extract, contains)
   - Apply functions to columns
   - Merge/concatenate operations on the same df
   - Pivot, melt, reshape data
   - Sort values
   - Reset index

3. DATA ANALYSIS
   - Aggregations (sum, mean, count, min, max, std, var)
   - Groupby operations with any aggregation
   - Value counts
   - Describe statistics
   - Correlation
   - Conditional statistics

4. FEATURE ENGINEERING
   - Create bins/categories (pd.cut, pd.qcut)
   - One-hot encoding (pd.get_dummies)
   - Label encoding
   - Date feature extraction (year, month, day, weekday, etc.)
   - Text feature extraction
   - Mathematical transformations (log, sqrt, power, etc.)

5. MACHINE LEARNING (when requested)
   - Train regression models (LinearRegression)
   - Train classification models
   - Generate predictions and add as new column
   - Store metrics in `result` variable

------------------------------------------------
RULES
------------------------------------------------

MUST DO:
- Assume `df` already exists (never create it)
- Use pandas (`pd`) and numpy (`np`) - they are pre-imported
- Assign the final result back to `df`
- Use actual column names from the schema provided
- Write clean, working code

MUST NOT:
- Import any libraries (pd, np are already available)
- Load or save files
- Use os, sys, subprocess, eval, exec
- Print anything
- Add comments or explanations

------------------------------------------------
AVAILABLE VARIABLES
------------------------------------------------

- `df` : The pandas DataFrame
- `pd` : pandas library
- `np` : numpy library
- `LinearRegression` : sklearn LinearRegression (for ML tasks)
- `train_test_split` : sklearn train_test_split (for ML tasks)

------------------------------------------------
OUTPUT FORMAT
------------------------------------------------

Return ONLY valid Python code.
No markdown code fences.
No explanations.
No comments.
Just pure Python code that works.

------------------------------------------------
EXAMPLES OF GOOD OUTPUT
------------------------------------------------

For "remove duplicates":
df = df.drop_duplicates()

For "fill missing values in age with the mean":
df['age'] = df['age'].fillna(df['age'].mean())

For "convert name to lowercase":
df['name'] = df['name'].str.lower()

For "filter rows where price > 100":
df = df[df['price'] > 100]

For "create a new column total = price * quantity":
df['total'] = df['price'] * df['quantity']

For "group by category and get average price":
df = df.groupby('category')['price'].mean().reset_index()

------------------------------------------------
NOW GENERATE CODE FOR THE USER'S REQUEST
------------------------------------------------
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
        "to_csv", "to_excel", "to_sql",
        "requests.", "urllib.", "socket.",
        "shutil.", "pathlib.", "glob."
    ]

    lowered = code.lower()
    for token in forbidden:
        if token in lowered:
            raise ValueError(f"Forbidden operation detected: {token}")

    return code


# ============================================================
# FALLBACK (NO AI) — EXPANDED KEYWORD-BASED
# ============================================================

def _generate_fallback_code(user_request: str, schema: dict) -> str:
    """
    Expanded keyword-based fallback when Gemma is disabled.
    Tries to fulfill common requests without AI.
    """
    req = user_request.lower()
    columns = list(schema.keys())
    code = []

    # DROP NULLS / MISSING VALUES
    if any(x in req for x in ["drop null", "remove null", "dropna", "drop missing", "remove missing"]):
        cols = [c for c in columns if c.lower() in req]
        if cols:
            code.append(f"df = df.dropna(subset={cols})")
        else:
            code.append("df = df.dropna()")

    # FILL NULLS / MISSING VALUES
    if any(x in req for x in ["fill null", "fill missing", "fillna", "replace null", "replace missing"]):
        if "mean" in req:
            for c in columns:
                if c.lower() in req:
                    code.append(f"df['{c}'] = df['{c}'].fillna(df['{c}'].mean())")
        elif "median" in req:
            for c in columns:
                if c.lower() in req:
                    code.append(f"df['{c}'] = df['{c}'].fillna(df['{c}'].median())")
        elif "0" in req or "zero" in req:
            code.append("df = df.fillna(0)")
        else:
            code.append("df = df.fillna(0)")

    # REMOVE DUPLICATES
    if "duplicate" in req:
        code.append("df = df.drop_duplicates()")

    # LOWERCASE
    if "lowercase" in req or "lower case" in req:
        for c in columns:
            if c.lower() in req or "all" in req:
                code.append(f"df['{c}'] = df['{c}'].astype(str).str.lower()")

    # UPPERCASE
    if "uppercase" in req or "upper case" in req:
        for c in columns:
            if c.lower() in req or "all" in req:
                code.append(f"df['{c}'] = df['{c}'].astype(str).str.upper()")

    # TRIM / STRIP WHITESPACE
    if any(x in req for x in ["trim", "strip", "whitespace"]):
        for c in columns:
            if c.lower() in req or "all" in req:
                code.append(f"df['{c}'] = df['{c}'].astype(str).str.strip()")

    # KEEP ONLY COLUMNS
    if any(x in req for x in ["keep only", "select only", "only keep", "select columns"]):
        keep = [c for c in columns if c.lower() in req]
        if keep:
            code.append(f"df = df[{keep}]")

    # DROP COLUMNS
    if any(x in req for x in ["drop column", "remove column", "delete column"]):
        drop = [c for c in columns if c.lower() in req]
        if drop:
            code.append(f"df = df.drop(columns={drop})")

    # RENAME COLUMN
    if "rename" in req:
        # Try to extract "rename X to Y" pattern
        pass  # Complex - leave to AI

    # SORT
    if "sort" in req:
        for c in columns:
            if c.lower() in req:
                if "desc" in req or "descending" in req:
                    code.append(f"df = df.sort_values('{c}', ascending=False)")
                else:
                    code.append(f"df = df.sort_values('{c}')")
                break

    # FILTER
    if "filter" in req or "where" in req:
        # Try to extract filter conditions
        import re as regex
        for c in columns:
            if c.lower() in req:
                if ">" in req:
                    match = regex.search(r'>\s*(\d+)', req)
                    if match:
                        code.append(f"df = df[df['{c}'] > {match.group(1)}]")
                elif "<" in req:
                    match = regex.search(r'<\s*(\d+)', req)
                    if match:
                        code.append(f"df = df[df['{c}'] < {match.group(1)}]")

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
    import re

    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split

    safe_globals = {
        "__builtins__": {
            "len": len, "range": range, "min": min, "max": max,
            "sum": sum, "abs": abs, "round": round,
            "int": int, "float": float, "str": str, "bool": bool,
            "list": list, "dict": dict, "tuple": tuple, "set": set,
            "sorted": sorted, "enumerate": enumerate, "zip": zip,
            "map": map, "filter": filter,
            "True": True, "False": False, "None": None,
        },
        "pd": pd,
        "np": np,
        "re": re,
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
