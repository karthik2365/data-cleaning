from fastapi import FastAPI, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from app.parser import parse_file
from app.cleaner import clean_record
from fastapi.middleware.cors import CORSMiddleware
import csv
import io
import json

app = FastAPI(title="Gemma Data Cleaner")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174", "http://localhost:5175", "http://127.0.0.1:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Rows", "X-Processed", "X-Count"],
)

# No row limit needed - deterministic cleaning is fast!

@app.post("/clean")
async def clean(
    file: UploadFile = File(...),
    output_format: str = Query(default="json", description="Output format: json or csv")
):
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
        # Process ALL rows - no limit needed with deterministic cleaning
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
        # text / CV
        total_rows = 1
        processed = 1
        cleaned = clean_record({"raw_text": parsed})
        if cleaned:
            results.append(cleaned)

    # Return CSV format if requested
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

    # Default: return JSON
    return {
        "count": len(results),
        "total_rows": total_rows,
        "processed": processed,
        "data": results
    }