from fastapi import FastAPI, UploadFile, File, Query, Form, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.parser import parse_file
from app.cleaner import clean_record
from app.code_generator import generate_cleaning_code, execute_cleaning_code
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import csv
import io
import json

app = FastAPI(
    title="Local AI Data Processor",
    description="""
    A local, AI-assisted data processing API where users upload datasets 
    and describe transformations in natural language.
    
    ## Architecture
    - **Local Gemma SLM**: Runs entirely on your machine - no data leaves your computer
    - **Human-in-the-Loop**: Review and approve generated code before execution
    - **Safe Execution**: Code runs in a sandboxed environment with strict validation
    - **Reproducible**: Same inputs always produce same outputs
    
    ## Workflow
    1. Upload a dataset (CSV, JSON, Excel)
    2. Describe your transformation in plain English
    3. Review the generated Python/pandas code
    4. Execute and download the processed data
    """,
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Rows", "X-Processed", "X-Count"],
)

# Store uploaded data temporarily (in production, use Redis or database)
_uploaded_data: Dict[str, pd.DataFrame] = {}


class CleaningRequest(BaseModel):
    """Request model for cleaning with user instructions"""
    session_id: str
    instruction: str


# ============================================================
# ENDPOINT 1: Upload and Preview
# ============================================================
@app.post("/upload")
async def upload_and_preview(file: UploadFile = File(...)):
    """
    Upload a file and return schema + preview.
    User can then decide what cleaning to apply.
    """
    content = await file.read()
    
    # Parse the file
    parsed = parse_file(file=content, filename=file.filename)
    
    # Convert to DataFrame
    if isinstance(parsed, list):
        df = pd.DataFrame(parsed)
    elif isinstance(parsed, dict):
        df = pd.DataFrame([parsed])
    else:
        df = pd.DataFrame([{"raw_text": parsed}])
    
    # Generate session ID
    import uuid
    session_id = str(uuid.uuid4())[:8]
    
    # Store the dataframe
    _uploaded_data[session_id] = df
    
    # Get schema
    schema = {}
    for col in df.columns:
        schema[col] = str(df[col].dtype)
    
    # Get sample data (first 10 rows)
    sample = df.head(10).to_dict(orient='records')
    
    # Get statistics
    stats = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum())
    }
    
    return {
        "session_id": session_id,
        "filename": file.filename,
        "schema": schema,
        "sample_data": sample,
        "statistics": stats,
        "message": "Data uploaded. What would you like to do with it?"
    }


# ============================================================
# ENDPOINT 2: Generate Code (Preview)
# ============================================================
@app.post("/generate-code")
async def generate_code(request: CleaningRequest):
    """
    Generate cleaning code based on user instruction.
    Returns the code for preview before execution.
    """
    session_id = request.session_id
    instruction = request.instruction
    
    if session_id not in _uploaded_data:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
    
    df = _uploaded_data[session_id]
    
    # Get schema and sample for code generation
    schema = {col: str(df[col].dtype) for col in df.columns}
    sample = df.head(10).to_dict(orient='records')
    
    # Generate code
    try:
        code = generate_cleaning_code(schema, sample, instruction)
        return {
            "session_id": session_id,
            "instruction": instruction,
            "generated_code": code,
            "message": "Review the code below. Call /execute to run it."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Code generation failed: {str(e)}")


# ============================================================
# ENDPOINT 3: Execute Code
# ============================================================
@app.post("/execute")
async def execute_code(
    session_id: str = Form(...),
    code: str = Form(...),
    output_format: str = Form(default="json")
):
    """
    Execute the generated (or user-modified) cleaning code.
    Returns the cleaned data.
    """
    if session_id not in _uploaded_data:
        raise HTTPException(status_code=404, detail="Session not found. Please upload a file first.")
    
    df = _uploaded_data[session_id]
    
    try:
        # Execute the code
        result = execute_cleaning_code(df, code)
        
        # Handle new tuple return format (df, result_info)
        if isinstance(result, tuple):
            cleaned_df, result_info = result
        else:
            cleaned_df = result
            result_info = None
        
        # Update stored data with cleaned version
        _uploaded_data[session_id] = cleaned_df
        
        # Convert to output format
        results = cleaned_df.to_dict(orient='records')
        
        if output_format.lower() == "csv":
            output = io.StringIO()
            cleaned_df.to_csv(output, index=False)
            
            return StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": "attachment; filename=cleaned_data.csv",
                    "X-Total-Rows": str(len(cleaned_df)),
                }
            )
        
        response = {
            "count": len(results),
            "total_rows": len(cleaned_df),
            "columns": list(cleaned_df.columns),
            "data": results,
            "message": "Operation completed successfully!"
        }
        
        # Include ML/analysis results if available
        if result_info:
            response["analysis_result"] = result_info
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Execution failed: {str(e)}")


# ============================================================
# ENDPOINT 4: Quick Clean (Original - deterministic only)
# ============================================================
@app.post("/clean")
async def clean(
    file: UploadFile = File(...),
    output_format: str = Query(default="json", description="Output format: json or csv")
):
    """
    Quick clean endpoint - uses deterministic rules only.
    No AI, no user interaction needed.
    """
    content = await file.read()

    parsed = parse_file(
        file=content,
        filename=file.filename
    )

    results = []
    total_rows = 0
    processed = 0

    if isinstance(parsed, list):
        total_rows = len(parsed)
        for row in parsed:
            cleaned = clean_record(row)
            processed += 1
            if cleaned:
                results.append(cleaned)

    elif isinstance(parsed, dict):
        total_rows = 1
        processed = 1
        cleaned = clean_record(parsed)
        if cleaned:
            results.append(cleaned)

    else:
        total_rows = 1
        processed = 1
        cleaned = clean_record({"raw_text": parsed})
        if cleaned:
            results.append(cleaned)

    if output_format.lower() == "csv" and results:
        output = io.StringIO()
        if results:
            writer = csv.DictWriter(output, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=cleaned_data.csv",
                "X-Total-Rows": str(total_rows),
                "X-Processed": str(processed),
                "X-Count": str(len(results))
            }
        )

    return {
        "count": len(results),
        "total_rows": total_rows,
        "processed": processed,
        "data": results
    }


# ============================================================
# ENDPOINT 5: Clear Session
# ============================================================
@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear uploaded data for a session"""
    if session_id in _uploaded_data:
        del _uploaded_data[session_id]
        return {"message": "Session cleared"}
    raise HTTPException(status_code=404, detail="Session not found")