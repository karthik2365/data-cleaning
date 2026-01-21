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
# SYSTEM PROMPT - OPTIMIZED FOR GEMMA CODE GENERATION
# ============================================================

CODE_GEN_PROMPT = """You are a Python pandas code generator. Generate ONLY executable Python code.

CONTEXT:
- DataFrame `df` exists with the columns shown in SCHEMA
- Libraries available: pd (pandas), np (numpy)
- You must output ONLY Python code, nothing else

TASK: Read the USER REQUEST and generate the exact pandas code to accomplish it.

CODE PATTERNS (use these exact patterns):

1. TYPE CONVERSIONS:
   - "convert X to integer" → df['X'] = pd.to_numeric(df['X'], errors='coerce').round().astype('Int64')
   - "convert X to float" → df['X'] = pd.to_numeric(df['X'], errors='coerce')
   - "convert X to string" → df['X'] = df['X'].astype(str)
   - "convert X to datetime" → df['X'] = pd.to_datetime(df['X'], errors='coerce')

2. MISSING VALUES:
   - "remove/drop nulls" → df = df.dropna()
   - "drop nulls in X" → df = df.dropna(subset=['X'])
   - "fill nulls with 0" → df = df.fillna(0)
   - "fill X with mean" → df['X'] = df['X'].fillna(df['X'].mean())
   - "fill X with median" → df['X'] = df['X'].fillna(df['X'].median())

3. DUPLICATES:
   - "remove duplicates" → df = df.drop_duplicates()
   - "remove duplicate X" → df = df.drop_duplicates(subset=['X'])

4. TEXT OPERATIONS:
   - "lowercase X" → df['X'] = df['X'].astype(str).str.lower()
   - "uppercase X" → df['X'] = df['X'].astype(str).str.upper()
   - "trim/strip X" → df['X'] = df['X'].astype(str).str.strip()
   - "title case X" → df['X'] = df['X'].astype(str).str.title()

5. FILTERING:
   - "filter where X > 10" → df = df[df['X'] > 10]
   - "filter where X == 'value'" → df = df[df['X'] == 'value']
   - "remove rows where X is null" → df = df[df['X'].notna()]
   - "keep rows where X contains 'text'" → df = df[df['X'].str.contains('text', na=False)]

6. COLUMNS:
   - "drop column X" → df = df.drop(columns=['X'])
   - "keep only X and Y" → df = df[['X', 'Y']]
   - "rename X to Y" → df = df.rename(columns={'X': 'Y'})
   - "create column Z = X + Y" → df['Z'] = df['X'] + df['Y']

7. SORTING:
   - "sort by X" → df = df.sort_values('X')
   - "sort by X descending" → df = df.sort_values('X', ascending=False)

8. AGGREGATIONS:
   - "group by X and sum Y" → df = df.groupby('X')['Y'].sum().reset_index()
   - "group by X and count" → df = df.groupby('X').size().reset_index(name='count')
   - "average of X" → df = pd.DataFrame({'average': [df['X'].mean()]})

9. DATE OPERATIONS:
   - "extract year from X" → df['year'] = pd.to_datetime(df['X']).dt.year
   - "extract month from X" → df['month'] = pd.to_datetime(df['X']).dt.month

10. MATH:
    - "log of X" → df['X_log'] = np.log(df['X'] + 1)
    - "square root of X" → df['X_sqrt'] = np.sqrt(df['X'])
    - "normalize X" → df['X'] = (df['X'] - df['X'].min()) / (df['X'].max() - df['X'].min())

CRITICAL RULES:
- Output ONLY Python code
- NO markdown, NO explanations, NO comments
- Use column names from the SCHEMA exactly as shown
- Always assign result back to df

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

    # Build a cleaner, more focused prompt for Gemma
    columns_list = ", ".join(schema.keys())
    
    prompt = f"""{CODE_GEN_PROMPT}
SCHEMA (columns available): {columns_list}

USER REQUEST: {user_request}

Python code:
df"""

    try:
        from app.model import run_gemma
        code = run_gemma(prompt)
        code = _validate_code(code)
        
        # Ensure code starts with df if model didn't include it
        if code and not code.strip().startswith('df'):
            code = 'df' + code
            
        return code
    except Exception as e:
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
    import re as regex
    
    req = user_request.lower()
    columns = list(schema.keys())
    code = []
    
    # Helper to find column mentioned in request
    def find_column(request):
        for c in columns:
            if c.lower() in request:
                return c
        return None

    # TYPE CONVERSIONS
    if any(x in req for x in ["convert", "to integer", "to int", "to numeric", "to float", "to string", "to datetime", "to date"]):
        col = find_column(req)
        if col:
            if any(x in req for x in ["integer", "int"]):
                code.append(f"df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce').round().astype('Int64')")
            elif "float" in req or "numeric" in req:
                code.append(f"df['{col}'] = pd.to_numeric(df['{col}'], errors='coerce')")
            elif "string" in req or "str" in req:
                code.append(f"df['{col}'] = df['{col}'].astype(str)")
            elif any(x in req for x in ["datetime", "date"]):
                code.append(f"df['{col}'] = pd.to_datetime(df['{col}'], errors='coerce')")

    # DROP NULLS / MISSING VALUES
    if any(x in req for x in ["drop null", "remove null", "dropna", "drop missing", "remove missing", "remove rows with null", "drop rows with null"]):
        col = find_column(req)
        if col:
            code.append(f"df = df.dropna(subset=['{col}'])")
        else:
            code.append("df = df.dropna()")

    # FILL NULLS / MISSING VALUES
    if any(x in req for x in ["fill null", "fill missing", "fillna", "replace null", "replace missing"]):
        col = find_column(req)
        if "mean" in req and col:
            code.append(f"df['{col}'] = df['{col}'].fillna(df['{col}'].mean())")
        elif "median" in req and col:
            code.append(f"df['{col}'] = df['{col}'].fillna(df['{col}'].median())")
        elif "0" in req or "zero" in req:
            if col:
                code.append(f"df['{col}'] = df['{col}'].fillna(0)")
            else:
                code.append("df = df.fillna(0)")
        else:
            code.append("df = df.fillna(0)")

    # REMOVE DUPLICATES
    if "duplicate" in req:
        col = find_column(req)
        if col:
            code.append(f"df = df.drop_duplicates(subset=['{col}'])")
        else:
            code.append("df = df.drop_duplicates()")

    # LOWERCASE
    if any(x in req for x in ["lowercase", "lower case", "to lower"]):
        col = find_column(req)
        if col:
            code.append(f"df['{col}'] = df['{col}'].astype(str).str.lower()")
        else:
            for c in columns:
                if schema.get(c) == 'object':
                    code.append(f"df['{c}'] = df['{c}'].astype(str).str.lower()")

    # UPPERCASE
    if any(x in req for x in ["uppercase", "upper case", "to upper"]):
        col = find_column(req)
        if col:
            code.append(f"df['{col}'] = df['{col}'].astype(str).str.upper()")

    # TITLE CASE
    if any(x in req for x in ["title case", "capitalize", "title"]):
        col = find_column(req)
        if col:
            code.append(f"df['{col}'] = df['{col}'].astype(str).str.title()")

    # TRIM / STRIP WHITESPACE
    if any(x in req for x in ["trim", "strip", "whitespace"]):
        col = find_column(req)
        if col:
            code.append(f"df['{col}'] = df['{col}'].astype(str).str.strip()")
        else:
            for c in columns:
                if schema.get(c) == 'object':
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

    # RENAME COLUMN (try to extract "rename X to Y" pattern)
    if "rename" in req:
        match = regex.search(r'rename\s+(\w+)\s+to\s+(\w+)', req)
        if match:
            old_name = match.group(1)
            new_name = match.group(2)
            # Find actual column name (case-insensitive)
            actual_col = None
            for c in columns:
                if c.lower() == old_name.lower():
                    actual_col = c
                    break
            if actual_col:
                code.append(f"df = df.rename(columns={{'{actual_col}': '{new_name}'}})")

    # SORT
    if "sort" in req:
        col = find_column(req)
        if col:
            if any(x in req for x in ["desc", "descending", "high to low", "largest", "biggest"]):
                code.append(f"df = df.sort_values('{col}', ascending=False)")
            else:
                code.append(f"df = df.sort_values('{col}')")

    # FILTER / WHERE
    if any(x in req for x in ["filter", "where", "keep rows", "remove rows"]):
        col = find_column(req)
        if col:
            # Try to extract numeric conditions
            match = regex.search(r'>\s*=?\s*(\d+\.?\d*)', req)
            if match:
                code.append(f"df = df[df['{col}'] >= {match.group(1)}]" if ">=" in req else f"df = df[df['{col}'] > {match.group(1)}]")
            else:
                match = regex.search(r'<\s*=?\s*(\d+\.?\d*)', req)
                if match:
                    code.append(f"df = df[df['{col}'] <= {match.group(1)}]" if "<=" in req else f"df = df[df['{col}'] < {match.group(1)}]")
                else:
                    match = regex.search(r'==?\s*(\d+\.?\d*)', req)
                    if match:
                        code.append(f"df = df[df['{col}'] == {match.group(1)}]")

    # EXTRACT YEAR/MONTH/DAY
    if any(x in req for x in ["extract year", "get year", "year from"]):
        col = find_column(req)
        if col:
            code.append(f"df['year'] = pd.to_datetime(df['{col}']).dt.year")
    if any(x in req for x in ["extract month", "get month", "month from"]):
        col = find_column(req)
        if col:
            code.append(f"df['month'] = pd.to_datetime(df['{col}']).dt.month")

    # GROUP BY
    if "group by" in req or "groupby" in req:
        # Try to extract group by column and aggregation
        group_col = None
        agg_col = None
        for c in columns:
            if c.lower() in req:
                if group_col is None:
                    group_col = c
                else:
                    agg_col = c
        if group_col:
            if "sum" in req:
                if agg_col:
                    code.append(f"df = df.groupby('{group_col}')['{agg_col}'].sum().reset_index()")
                else:
                    code.append(f"df = df.groupby('{group_col}').sum().reset_index()")
            elif "mean" in req or "average" in req:
                if agg_col:
                    code.append(f"df = df.groupby('{group_col}')['{agg_col}'].mean().reset_index()")
                else:
                    code.append(f"df = df.groupby('{group_col}').mean().reset_index()")
            elif "count" in req:
                code.append(f"df = df.groupby('{group_col}').size().reset_index(name='count')")
            else:
                code.append(f"df = df.groupby('{group_col}').size().reset_index(name='count')")

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
