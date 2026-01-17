"""
Code Generator Module
Uses Gemma to generate safe Python code for data cleaning, analysis, and ML tasks.
"""
from app.config import ENABLE_GEMMA

# System prompt for code generation
CODE_GEN_PROMPT = """You are a Python code generator for data operations.

You work with a pandas DataFrame called `df` that already exists.
The user will describe what they want to do with the data.

YOUR CAPABILITIES:
1. DATA CLEANING: Drop nulls, remove duplicates, normalize values, trim whitespace
2. DATA TRANSFORMATION: Create columns, filter rows, convert types, rename columns
3. DATA ANALYSIS: Statistics, groupby, correlations, aggregations
4. MACHINE LEARNING: Train models, make predictions, evaluate performance

AVAILABLE LIBRARIES (pre-loaded):
- pandas as pd
- numpy as np
- sklearn (LinearRegression, DecisionTreeRegressor, RandomForestRegressor, train_test_split, etc.)

STRICT RULES:
- Assume `df` already exists with the data
- Do NOT use import statements (libraries are pre-loaded)
- Do NOT load or save files
- Do NOT use os, sys, subprocess, eval, exec
- Store final results in `df` or `result` variable
- For ML predictions, add predictions as a new column to df

OUTPUT FORMAT:
Return ONLY valid Python code. No markdown. No explanations. No comments.
No import statements needed - all libraries are pre-loaded.

EXAMPLES:

User: "Predict BMI using glucose and pregnancies"
Code:
X = df[['Glucose', 'Pregnancies']]
y = df['BMI']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LinearRegression()
model.fit(X_train, y_train)
df['BMI_Predicted'] = model.predict(X)
result = {'model': 'LinearRegression', 'score': model.score(X_test, y_test)}

User: "Remove rows where age is null"
Code:
df = df.dropna(subset=['Age'])

User: "Keep only columns: Name, Age, Salary"
Code:
df = df[['Name', 'Age', 'Salary']]"""


def generate_cleaning_code(schema: dict, sample_data: list, user_request: str) -> str:
    """
    Generate Python code based on user request.
    
    Args:
        schema: Dict with column names and types
        sample_data: First 10 rows of data
        user_request: Natural language instruction
    
    Returns:
        Python code string to execute
    """
    if not ENABLE_GEMMA:
        # Fallback: return basic code when Gemma is disabled
        return _generate_fallback_code(user_request, schema)
    
    # Build the prompt
    prompt = f"""{CODE_GEN_PROMPT}

DATASET SCHEMA:
{_format_schema(schema)}

SAMPLE DATA (first 10 rows):
{_format_sample(sample_data)}

USER REQUEST:
{user_request}

PYTHON CODE:"""
    
    try:
        from app.model import run_gemma
        code = run_gemma(prompt)
        
        # Validate and sanitize the code
        validated_code = _validate_code(code)
        return validated_code
    except Exception as e:
        # Fallback to basic code generation
        return _generate_fallback_code(user_request)


def _format_schema(schema: dict) -> str:
    """Format schema for prompt"""
    lines = []
    for col, dtype in schema.items():
        lines.append(f"- {col}: {dtype}")
    return "\n".join(lines)


def _format_sample(sample_data: list) -> str:
    """Format sample data for prompt"""
    if not sample_data:
        return "No sample data available"
    
    # Get column headers from first row
    if sample_data:
        headers = list(sample_data[0].keys())
        lines = [" | ".join(headers)]
        lines.append("-" * len(lines[0]))
        
        for row in sample_data[:5]:  # Limit to 5 rows in prompt
            values = [str(row.get(h, ""))[:20] for h in headers]  # Truncate long values
            lines.append(" | ".join(values))
        
        return "\n".join(lines)
    return "No data"


def _validate_code(code: str) -> str:
    """
    Validate generated code for safety.
    Remove any dangerous operations.
    """
    # Strip markdown code blocks if present
    code = code.strip()
    if code.startswith("```python"):
        code = code[9:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    code = code.strip()
    
    # List of forbidden patterns
    forbidden = [
        'import os',
        'import sys',
        'import subprocess',
        'from os',
        'from sys',
        'from subprocess',
        '__import__',
        'eval(',
        'exec(',
        'open(',
        'file(',
        'input(',
        'raw_input(',
        '.to_csv(',
        '.to_excel(',
        '.to_sql(',
        '.to_pickle(',
        'read_csv',
        'read_excel',
        'read_json',
        'read_sql',
        'requests.',
        'urllib.',
        'socket.',
        'shutil.',
        'glob.',
        'pathlib.',
    ]
    
    code_lower = code.lower()
    for pattern in forbidden:
        if pattern.lower() in code_lower:
            raise ValueError(f"Forbidden operation detected: {pattern}")
    
    # Remove import statements (pandas is pre-loaded as 'pd')
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            continue  # Skip import statements
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines).strip()


def _generate_fallback_code(user_request: str, schema: dict = None) -> str:
    """
    Generate code without AI using keyword matching.
    Handles cleaning, analysis, and basic ML tasks.
    ALWAYS applies standard cleaning first: remove duplicates, drop nulls, trim whitespace, lowercase.
    """
    request_lower = user_request.lower()
    code_lines = []
    columns = list(schema.keys()) if schema else []
    
    # =====================
    # ALWAYS APPLY STANDARD CLEANING FIRST
    # =====================
    code_lines.append("# Standard cleaning operations")
    code_lines.append("# 1. Remove duplicates")
    code_lines.append("df = df.drop_duplicates()")
    code_lines.append("")
    code_lines.append("# 2. Drop null values")
    code_lines.append("df = df.dropna()")
    code_lines.append("")
    code_lines.append("# 3. Trim whitespace from string columns")
    code_lines.append("for col in df.select_dtypes(include=['object']).columns:")
    code_lines.append("    df[col] = df[col].str.strip()")
    code_lines.append("")
    code_lines.append("# 4. Convert string columns to lowercase")
    code_lines.append("for col in df.select_dtypes(include=['object']).columns:")
    code_lines.append("    df[col] = df[col].str.lower()")
    code_lines.append("")
    
    # =====================
    # ML / PREDICTION TASKS
    # =====================
    if any(x in request_lower for x in ['predict', 'regression', 'forecast', 'estimate']):
        # Try to extract target and features from request
        target = None
        features = []
        
        # Common patterns: "predict X using Y and Z"
        if ' using ' in request_lower:
            parts = request_lower.split(' using ')
            # Find target (what to predict)
            for col in columns:
                if col.lower() in parts[0]:
                    target = col
                    break
            # Find features
            for col in columns:
                if col.lower() in parts[1] and col != target:
                    features.append(col)
        
        # If we found target and features, generate ML code
        if target and features:
            code_lines.append(f"# Predicting {target} using {', '.join(features)}")
            code_lines.append(f"X = df[[{', '.join([repr(f) for f in features])}]].dropna()")
            code_lines.append(f"y = df.loc[X.index, '{target}']")
            code_lines.append("")
            code_lines.append("X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)")
            code_lines.append("")
            code_lines.append("model = LinearRegression()")
            code_lines.append("model.fit(X_train, y_train)")
            code_lines.append("")
            code_lines.append(f"df['{target}_Predicted'] = np.nan")
            code_lines.append(f"df.loc[X.index, '{target}_Predicted'] = model.predict(X)")
            code_lines.append("")
            code_lines.append("score = model.score(X_test, y_test)")
            code_lines.append(f"result = {{'model': 'LinearRegression', 'r2_score': round(score, 4), 'target': '{target}', 'features': {features}}}")
            return "\n".join(code_lines)
    
    # =====================
    # KEEP ONLY COLUMNS
    # =====================
    if any(x in request_lower for x in ['keep only', 'select only', 'only keep', 'only columns']):
        # Find mentioned columns
        keep_cols = [col for col in columns if col.lower() in request_lower]
        if keep_cols:
            code_lines.append(f"# User requested: keep only specific columns")
            code_lines.append(f"df = df[[{', '.join([repr(c) for c in keep_cols])}]]")
            return "\n".join(code_lines)
    
    # =====================
    # DROP COLUMNS
    # =====================
    if any(x in request_lower for x in ['drop column', 'remove column', 'delete column']):
        drop_cols = [col for col in columns if col.lower() in request_lower]
        if drop_cols:
            code_lines.append(f"# User requested: drop specific columns")
            code_lines.append(f"df = df.drop(columns={drop_cols})")
            return "\n".join(code_lines)
    
    # =====================
    # ADDITIONAL USER-SPECIFIC OPERATIONS
    # =====================
    
    # Uppercase (if user specifically wants uppercase instead of lowercase)
    if any(x in request_lower for x in ['uppercase', 'upper case']):
        code_lines.append("# User requested: convert to uppercase (overriding default lowercase)")
        code_lines.append("for col in df.select_dtypes(include=['object']).columns:")
        code_lines.append("    df[col] = df[col].str.upper()")
    
    # Fill nulls instead of dropping (if user prefers filling)
    if 'fill' in request_lower and any(x in request_lower for x in ['null', 'na', 'missing']):
        code_lines.append("# User requested: fill nulls instead of dropping")
        if 'zero' in request_lower or '0' in request_lower:
            code_lines.append("df = df.fillna(0)")
        elif 'empty' in request_lower or '""' in request_lower:
            code_lines.append("df = df.fillna('')")
        else:
            code_lines.append("df = df.fillna(method='ffill')")
    
    # Return with standard cleaning already applied
    return "\n".join(code_lines)


def execute_cleaning_code(df, code: str):
    """
    Safely execute the generated code (cleaning, analysis, ML).
    
    Args:
        df: pandas DataFrame
        code: Python code string to execute
    
    Returns:
        tuple: (DataFrame, result_dict or None)
    """
    import pandas as pd
    import numpy as np
    
    # Import sklearn components
    try:
        from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
        from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
        from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
        from sklearn.model_selection import train_test_split
        from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder
        from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
        sklearn_available = True
    except ImportError:
        sklearn_available = False
    
    # Remove import statements from code
    lines = code.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            continue
        cleaned_lines.append(line)
    clean_code = '\n'.join(cleaned_lines).strip()
    
    # Create a safe namespace
    safe_globals = {
        '__builtins__': {
            'len': len,
            'range': range,
            'str': str,
            'int': int,
            'float': float,
            'bool': bool,
            'list': list,
            'dict': dict,
            'tuple': tuple,
            'set': set,
            'min': min,
            'max': max,
            'sum': sum,
            'abs': abs,
            'round': round,
            'sorted': sorted,
            'enumerate': enumerate,
            'zip': zip,
            'map': map,
            'filter': filter,
            'isinstance': isinstance,
            'type': type,
            'hasattr': hasattr,
            'getattr': getattr,
            'print': print,
            'True': True,
            'False': False,
            'None': None,
        },
        'pd': pd,
        'pandas': pd,
        'np': np,
        'numpy': np,
    }
    
    # Add sklearn if available
    if sklearn_available:
        safe_globals.update({
            'LinearRegression': LinearRegression,
            'LogisticRegression': LogisticRegression,
            'Ridge': Ridge,
            'Lasso': Lasso,
            'DecisionTreeRegressor': DecisionTreeRegressor,
            'DecisionTreeClassifier': DecisionTreeClassifier,
            'RandomForestRegressor': RandomForestRegressor,
            'RandomForestClassifier': RandomForestClassifier,
            'train_test_split': train_test_split,
            'StandardScaler': StandardScaler,
            'MinMaxScaler': MinMaxScaler,
            'LabelEncoder': LabelEncoder,
            'mean_squared_error': mean_squared_error,
            'r2_score': r2_score,
            'accuracy_score': accuracy_score,
        })
    
    safe_locals = {
        'df': df.copy(),
        'result': None
    }
    
    try:
        # Execute the code
        exec(clean_code, safe_globals, safe_locals)
        
        # Get results
        result_df = safe_locals.get('df', df)
        result_info = safe_locals.get('result', None)
        
        return result_df, result_info
    except Exception as e:
        raise RuntimeError(f"Code execution failed: {str(e)}")
