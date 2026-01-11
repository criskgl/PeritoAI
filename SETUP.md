# Setup Instructions

## Quick Start

1. **Install dependencies:**
   ```bash
   # On macOS, use pip3 instead of pip
   pip3 install -r requirements.txt
   
   # Or use python3 -m pip (recommended)
   python3 -m pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   # Create .env file
   echo "GEMINI_API_KEY=your_api_key_here" > .env
   ```

3. **Add policy PDFs:**
   - Place PDF files in `data/policies/`
   - Recommended naming: `POLIZA_12345.pdf` or `poliza_12345.pdf`

4. **Run Streamlit app:**
   ```bash
   streamlit run app.py
   ```

## Note on LangChain Versions

If you encounter import errors related to LangChain, you may need to adjust the import statements based on your LangChain version:

- For LangChain >= 0.2.0, some imports may need to be updated
- `langchain.vectorstores` might become `langchain_community.vectorstores`
- `langchain.schema` might become `langchain_core.messages`

If issues occur, try:
```bash
pip install langchain==0.1.0 langchain-google-genai==0.0.5
```

Or update the imports in the code to match newer LangChain structure.

## Troubleshooting

### Import Errors
- Ensure all dependencies are installed: `pip3 install -r requirements.txt` (or `python3 -m pip install -r requirements.txt`)
- Check Python version: `python3 --version` (should be 3.10+)
- On macOS, use `pip3` or `python3 -m pip` instead of `pip`

### API Key Issues
- Verify `.env` file exists and contains `GEMINI_API_KEY=...`
- Ensure no extra spaces around the `=` sign

### PDF Reading Errors
- Ensure PyMuPDF (fitz) is installed: `pip install pymupdf`
- Verify PDF files are not password-protected or corrupted
