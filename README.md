# 🧪 Local AI Data Processor

A local, AI-assisted data processing web application where users upload a dataset and describe how they want it cleaned or transformed in natural language. A Small Language Model (Gemma) runs locally to generate safe Python (pandas) code based on the user's request, which is then validated and executed in a controlled environment to produce the final dataset.

**The system follows a human-in-the-loop design, prioritizing transparency, reproducibility, and offline execution over black-box automation.**

![Architecture](https://img.shields.io/badge/Architecture-Human--in--the--Loop-green)
![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local-blue)
![AI](https://img.shields.io/badge/AI-Gemma%20SLM-orange)

---

## 🎯 Key Principles

| Principle | Description |
|-----------|-------------|
| **🔒 Privacy First** | Your data never leaves your machine. Gemma runs 100% locally. |
| **👁️ Full Transparency** | See exactly what code will run. No black boxes. |
| **👤 Human-in-the-Loop** | AI suggests code, but YOU review and approve before execution. |
| **🔄 Reproducible** | Same input + same code = same output. Every time. |
| **📴 Offline Capable** | Works without internet after initial model download. |
| **🛡️ Safe Execution** | Code runs in a sandboxed environment with restricted capabilities. |

---

## 🔄 How It Works

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Upload    │────▶│ Describe in      │────▶│  Local Gemma    │
│   Dataset   │     │ Plain English    │     │  Generates Code │
└─────────────┘     └──────────────────┘     └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Download   │◀────│  Execute in      │◀────│  YOU Review &   │
│   Result    │     │  Sandbox         │     │  Approve Code   │
└─────────────┘     └──────────────────┘     └─────────────────┘
```

1. **Upload** your dataset (CSV, JSON, Excel)
2. **Describe** what you want in natural language (e.g., "Remove duplicates and fill null values with 0")
3. **Review** the generated Python/pandas code
4. **Edit** if needed (you have full control)
5. **Execute** safely in a sandboxed environment
6. **Download** your transformed data

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- 8GB+ RAM recommended (for running Gemma locally)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server (Gemma will download on first run)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Open http://localhost:5173 in your browser.

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Local AI** | Gemma 2 (2B) | Natural language to code translation |
| **Backend** | FastAPI | API endpoints, file handling |
| **Data Processing** | pandas, NumPy | Data manipulation and transformation |
| **ML (Optional)** | scikit-learn | Predictions and analysis |
| **Frontend** | React + Vite | User interface |
| **Sandbox** | Restricted exec() | Safe code execution |

---

## 📝 Example Requests

Here are some natural language commands you can use:

| Request | What It Does |
|---------|--------------|
| "Remove duplicate rows" | `df = df.drop_duplicates()` |
| "Drop rows where age is null" | `df = df.dropna(subset=['age'])` |
| "Convert name to lowercase" | `df['name'] = df['name'].str.lower()` |
| "Fill missing values with 0" | `df = df.fillna(0)` |
| "Keep only name and email columns" | `df = df[['name', 'email']]` |
| "Filter rows where price > 100" | `df = df[df['price'] > 100]` |

---

## 🔐 Safety Guarantees

### Code Validation
All generated code is validated against a strict blocklist before execution:
- ❌ No imports
- ❌ No file system access (`open`, `read`, `write`)
- ❌ No network access (`requests`, `urllib`)
- ❌ No system commands (`os`, `sys`, `subprocess`)
- ❌ No `eval()` or `exec()` (except our controlled sandbox)

### Sandboxed Execution
Code runs with:
- Limited Python builtins (only `len`, `range`, `min`, `max`, `sum`, `abs`, `round`)
- Pre-imported `pandas` and `numpy` only
- No access to the actual file system or network

---

## 📁 Project Structure

```
datacleaning/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI endpoints
│   │   ├── model.py          # Local Gemma handler
│   │   ├── code_generator.py # NL to code translation
│   │   ├── cleaner.py        # Rule-based cleaning
│   │   ├── parser.py         # File parsing
│   │   ├── config.py         # Configuration
│   │   └── schemas.py        # Pydantic models
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js            # Backend API calls
│   │   └── components/
│   │       ├── DataCleaner.jsx  # Main processing UI
│   │       ├── hero.jsx
│   │       └── ...
│   └── package.json
│
└── README.md
```

---

## 🔧 Configuration

Edit `backend/app/config.py`:

```python
# Enable/disable AI (set False for rule-based only)
ENABLE_GEMMA = True

# Model to use (runs locally)
MODEL_NAME = "google/gemma-2-2b-it"

# Generation settings
GENERATION_CONFIG = {
    "max_new_tokens": 512,
    "do_sample": False,
    "temperature": 0.1,
}
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

## 📄 License

MIT License - Feel free to use this for any purpose.

---

## 🙏 Acknowledgments

- [Google Gemma](https://ai.google.dev/gemma) - The local SLM powering natural language understanding
- [Hugging Face Transformers](https://huggingface.co/docs/transformers) - Model loading and inference
- [FastAPI](https://fastapi.tiangolo.com/) - High-performance Python web framework
- [pandas](https://pandas.pydata.org/) - Data manipulation library
