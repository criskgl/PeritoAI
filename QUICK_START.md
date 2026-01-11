# Quick Start Guide - PeritoAI

## ✅ Current Status
- ✅ App is running correctly
- ✅ Dependencies installed
- ✅ Code is ready

## 🚀 Next Steps (5 minutes)

### Step 1: Verify API Key (30 seconds)
```bash
# Check if .env has your API key
cat .env

# If not, add it:
echo "GEMINI_API_KEY=your_actual_key_here" > .env
```
**Get API Key**: https://makersuite.google.com/app/apikey

### Step 2: Add a Test Policy PDF (1 minute)
```bash
# Copy any insurance policy PDF to:
cp /path/to/your/policy.pdf data/policies/POLIZA_TEST001.pdf
```
**Note**: Use naming like `POLIZA_12345.pdf` where `12345` is the Policy ID

### Step 3: Index the Policy (1 minute)
In Streamlit UI:
1. Click **"🔄 Inicializar Motor RAG"** (sidebar)
2. Click **"📥 Indexar Pólizas PDF"** (sidebar)
3. Wait for success message

### Step 4: Generate First Report (2 minutes)
Fill in the form:
- **ID de Póliza**: `TEST001` (from filename)
- **Notas de Campo**: 
  ```
  El asegurado reportó daños por agua en el techo. 
  Inspección realizada: humedad visible, manchado en paredes, 
  daños en parquet. Origen: gotera en tejado por lluvias intensas.
  ```
- Click **"🚀 Generar Informe"**

### Step 5: Download Report (30 seconds)
- Review generated report in Spanish
- Click **"📄 Generar y Descargar PDF"** for formatted PDF

## 📋 What Each Section Does

### RAG Engine (`engine/rag_engine.py`)
- Extracts text from PDFs
- Chunks and indexes into ChromaDB
- Searches relevant policy sections

### Generator (`engine/generator.py`)
- Uses Gemini 1.5 Pro to generate reports
- Prompts in English, output in Spanish
- Creates structured 5-section reports

### PDF Exporter (`engine/pdf_exporter.py`)
- Formats reports as professional PDFs
- Adds headers, sections, metadata

## 🎯 Tips for Best Results

1. **Policy PDFs**:
   - Use text-based PDFs (not scanned images)
   - Ensure policies contain coverage clauses
   - Name files consistently: `POLIZA_[ID].pdf`

2. **Field Notes**:
   - Be specific about damages
   - Include dates, locations, causes
   - Mention any observations relevant to coverage

3. **Policy ID**:
   - Must match filename exactly
   - Example: File `POLIZA_12345.pdf` → Policy ID: `12345`

4. **Query Context** (Optional):
   - Use to focus search on specific topics
   - Example: "cobertura agua daños" for water damage coverage

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "GEMINI_API_KEY not found" | Check `.env` file exists and has correct key |
| "No PDF files found" | Add PDFs to `data/policies/` directory |
| "No relevant sections found" | Verify Policy ID matches filename, reindex |
| "Error generating report" | Check API key is valid, internet connection OK |

## 📚 Full Documentation
- `README.md` - Complete project documentation
- `NEXT_STEPS.md` - Detailed setup instructions
- `SETUP.md` - Installation and configuration guide

## 🎉 You're Ready!

Your PeritoAI MVP is fully functional. Start adding policy PDFs and generating reports!
