import pandas as pd
import pdfplumber
from docx import Document
import json
from io import BytesIO


def parse_file(file: bytes, filename: str):
    file_like = BytesIO(file)
    
    if filename.endswith(".csv"):
        return pd.read_csv(file_like).to_dict(orient="records")

    if filename.endswith(".xlsx"):
        return pd.read_excel(file_like).to_dict(orient="records")

    if filename.endswith(".json"):
        return json.load(file_like)

    if filename.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_like) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text

    if filename.endswith(".docx"):
        doc = Document(file_like)
        return "\n".join(p.text for p in doc.paragraphs)

    raise ValueError("Unsupported file format")