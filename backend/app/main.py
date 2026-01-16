from fastapi import FastAPI, UploadFile, File, Query
from app.parser import parse_file
from app.cleaner import clean_record
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gemma Data Cleaner")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_ROWS = 5  # Limit rows to process (CPU inference is slow)

@app.post("/clean")
async def clean(file: UploadFile = File(...)):
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
        # Limit to MAX_ROWS for CPU performance
        for row in parsed[:MAX_ROWS]:
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

    return {
        "count": len(results),
        "total_rows": total_rows,
        "processed": processed,
        "data": results
    }