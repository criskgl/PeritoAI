# PeritoAI MVP

A Python-based RAG (Retrieval-Augmented Generation) application to automate the creation of insurance adjuster reports (Informes Periciales) in Spanish.

## Project Overview

PeritoAI generates professional insurance adjuster reports by:
1. Indexing insurance policy PDFs from `/data/policies/`
2. Using RAG to retrieve relevant policy clauses based on field notes
3. Generating structured reports in Spanish following Spanish insurance industry standards
4. Exporting reports as PDF documents

## Technical Stack

- **Language**: Python 3.10+
- **LLM**: Google Gemini 1.5 Pro (via `google-generativeai`)
- **Orchestration**: LangChain
- **Vector Database**: ChromaDB (local persistent storage)
- **Frontend**: Streamlit
- **Backend API**: FastAPI (with WhatsApp webhook support)
- **PDF Processing**: PyMuPDF (fitz)
- **PDF Generation**: fpdf2

## Project Structure

```
/perito-ai
├── app.py                # Streamlit UI
├── main.py               # FastAPI server & Webhook skeleton
├── engine/
│   ├── __init__.py
│   ├── rag_engine.py      # PDF indexing & vector search
│   ├── generator.py       # Prompt engineering & LLM logic
│   └── pdf_exporter.py    # PDF creation logic
├── data/
│   ├── policies/          # Source PDFs (place your policy PDFs here)
│   ├── chroma_db/         # Persisted Vector DB (auto-generated)
│   └── reports/           # Generated reports (auto-generated)
├── .env                   # Environment variables (GEMINI_API_KEY)
└── requirements.txt       # Python dependencies
```

## Installation

1. **Clone the repository** (or navigate to the project directory)

2. **Create a virtual environment** (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
# On macOS, use pip3 instead of pip
pip3 install -r requirements.txt

# Or use python3 -m pip
python3 -m pip install -r requirements.txt
```

4. **Set up environment variables**:
   - Create a `.env` file in the project root
   - Add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   - Optionally, for WhatsApp webhook:
   ```
   WHATSAPP_VERIFY_TOKEN=your_verification_token
   ```

5. **Add policy PDFs**:
   - Place your insurance policy PDFs in `/data/policies/`
   - Recommended naming: `POLIZA_12345.pdf` or `poliza_12345.pdf`
   - The Policy ID will be extracted from the filename

## Usage

### Streamlit UI (Primary Interface)

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your browser. Steps:

1. **Initialize RAG Engine**: Click "Inicializar Motor RAG" in the sidebar
2. **Index Policies**: Click "Indexar Pólizas PDF" to process PDFs in `/data/policies/`
3. **Generate Report**:
   - Enter Policy ID (must match PDF filename)
   - Optionally enter Claim ID
   - Enter field notes (adjuster's observations)
   - Optionally specify search context
   - Click "Generar Informe"
4. **Download**: Download the generated report as text or PDF

### FastAPI Server

Run the FastAPI server:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

#### API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health status
- `POST /api/generate-report` - Generate report (returns JSON)
- `POST /api/generate-report-pdf` - Generate report (returns PDF)
- `POST /webhook` - WhatsApp webhook endpoint (ready for Meta Cloud API)
- `POST /api/index-policies?overwrite=false` - Index PDF policies

#### Example API Request

```bash
curl -X POST "http://localhost:8000/api/generate-report" \
  -H "Content-Type: application/json" \
  -d '{
    "field_notes": "El asegurado reportó daños por agua en el techo...",
    "policy_id": "POLIZA_12345",
    "claim_id": "SIN-2024-001",
    "query_context": "cobertura agua daños"
  }'
```

## Report Structure

Generated reports follow Spanish insurance standards with these sections:

1. **IDENTIFICACIÓN** (Identification)
   - Policy details, Claim ID, Insured party, Dates

2. **ANTECEDENTES** (Background)
   - Summary of incident and damages from field notes

3. **ANÁLISIS DE CAUSALIDAD** (Causality Analysis)
   - Technical "Nexo Causal" evaluation
   - Cause-effect relationship assessment

4. **ANÁLISIS DE COBERTURA** (Coverage Analysis)
   - Comparison of damages with policy clauses
   - Coverage assessment and exclusions

5. **TASACIÓN Y PROPUESTA** (Valuation and Proposal)
   - Economic estimation
   - Final verdict and recommended settlement

## Configuration

### RAG Engine Settings

In `engine/rag_engine.py`, you can adjust:
- `chunk_size`: Text chunk size (default: 1000)
- `chunk_overlap`: Overlap between chunks (default: 200)
- `embedding_model`: Embedding model name (default: `models/text-embedding-004`)

### Generator Settings

In `engine/generator.py`, you can adjust:
- `model_name`: LLM model (default: `gemini-1.5-pro`)
- `temperature`: Generation temperature (default: 0.3)

## WhatsApp Webhook (Future Integration)

The `/webhook` endpoint is prepared to receive payloads from Meta WhatsApp Cloud API. Currently, it:
- Logs incoming payloads
- Handles webhook verification (GET requests)
- Provides structure for processing WhatsApp messages

To complete the integration:
1. Configure webhook URL in Meta Business Manager
2. Implement message parsing in `main.py`
3. Integrate with WhatsApp Business API to send responses

## Troubleshooting

### "GEMINI_API_KEY not found"
- Ensure `.env` file exists in project root
- Check that the API key is correctly set

### "No PDF files found in data/policies"
- Ensure PDF files are placed in `/data/policies/` directory
- Check file naming matches expected format

### "No relevant sections found in policy"
- Verify Policy ID matches the PDF filename
- Try reindexing policies with "Reindexar (Sobrescribir)"
- Check that the PDF contains readable text

### ChromaDB errors
- Delete `/data/chroma_db/` directory and reindex
- Ensure write permissions on the data directory

## Development

### Code Style
- All code (variables, functions, comments, documentation) must be in English
- Reports are generated in Spanish using insurance terminology

### Adding New Features
- RAG Engine: Modify `engine/rag_engine.py`
- Report Generation: Modify prompts in `engine/generator.py`
- PDF Export: Modify formatting in `engine/pdf_exporter.py`
- UI: Modify `app.py` for Streamlit interface
- API: Modify `main.py` for FastAPI endpoints

## License

[Add your license here]

## Author

PeritoAI MVP
