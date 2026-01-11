# Next Steps - Getting Started with PeritoAI

Congratulations! Your app is running. Now let's set it up and generate your first report.

## Step 1: Configure API Key

1. **Create `.env` file** in the project root:
   ```bash
   cd /Users/crisgomezlopez/Projects/peritoAi
   ```

2. **Add your Google Gemini API Key**:
   ```bash
   echo "GEMINI_API_KEY=your_actual_api_key_here" > .env
   ```
   
   Or create/edit the file manually:
   ```bash
   nano .env
   # Add: GEMINI_API_KEY=your_actual_api_key_here
   ```

3. **Get your API Key** (if you don't have one):
   - Visit: https://makersuite.google.com/app/apikey
   - Or: https://aistudio.google.com/app/apikey
   - Create a new API key
   - Copy it to your `.env` file

## Step 2: Add Policy PDFs

1. **Place your insurance policy PDFs** in the `data/policies/` directory:
   ```bash
   # Example: Copy your PDFs
   cp /path/to/your/policy.pdf data/policies/POLIZA_12345.pdf
   ```

2. **Naming Convention**:
   - Recommended: `POLIZA_12345.pdf` or `poliza_12345.pdf`
   - The system extracts Policy ID from filename (e.g., `12345`)
   - Policy ID should be unique for each policy

3. **Verify PDFs are readable**:
   - Ensure PDFs are not password-protected
   - Ensure PDFs contain text (not just images)
   - If PDFs are scanned images, you may need OCR first

## Step 3: Initialize and Index Policies

1. **Open the Streamlit app** (if not already open):
   ```bash
   streamlit run app.py
   ```

2. **In the Streamlit UI sidebar**:
   - Click **"🔄 Inicializar Motor RAG"** button
   - Wait for "Motor RAG inicializado correctamente" message

3. **Index the Policies**:
   - Click **"📥 Indexar Pólizas PDF"** button
   - Wait for indexing to complete
   - You should see: "Pólizas indexadas correctamente"

4. **Verify indexing**:
   - Check that `data/chroma_db/` directory contains files
   - If errors occur, check PDFs are valid and contain text

## Step 4: Generate Your First Report

1. **Fill in the form** in the main interface:

   - **ID de Póliza**: Enter the Policy ID (extracted from filename, e.g., `12345`)
   
   - **ID de Siniestro** (Optional): Enter claim ID, e.g., `SIN-2024-001`
   
   - **Notas de Campo del Perito**: Enter detailed field notes in Spanish or English, for example:
     ```
     El asegurado reportó daños por agua en el techo de la vivienda. 
     La inspección realizada el día 15/03/2024 reveló:
     - Humedad visible en el techo del salón principal
     - Manchado en las paredes
     - Daños estimados en el parquet del suelo
     - Posible origen: gotera en el tejado debido a lluvias intensas
     ```
   
   - **Contexto de Búsqueda** (Optional): Enter specific keywords to search in policy, e.g., `cobertura agua daños`

2. **Click "🚀 Generar Informe"** button

3. **Wait for generation** (may take 30-60 seconds):
   - The system will search relevant policy sections
   - Generate the report in Spanish using Gemini 1.5 Pro

4. **Review the generated report**:
   - Check all 5 sections are present:
     - IDENTIFICACIÓN
     - ANTECEDENTES
     - ANÁLISIS DE CAUSALIDAD
     - ANÁLISIS DE COBERTURA
     - TASACIÓN Y PROPUESTA

5. **Download the report**:
   - Click **"📥 Descargar como Texto (.txt)"** for text version
   - Click **"📄 Generar y Descargar PDF"** for formatted PDF

## Step 5: Testing with Sample Data

If you don't have actual policy PDFs yet, you can test with:

### Sample Field Notes (Spanish):
```
Siniestro reportado el día 10 de enero de 2024. El asegurado indica que 
se produjo una inundación en su vivienda debido a una rotura de tubería 
en el baño principal. Durante la inspección se observaron:

- Daños por agua en el suelo del baño y pasillo adyacente
- Parquet hinchado y levantado en varias zonas
- Manchado en las paredes hasta 30 cm de altura
- Posible afectación del mobiliario de baño

La rotura parece haberse producido por desgaste natural de las tuberías.
Los daños son visibles y cuantificables. Se requiere tasación completa.
```

### Sample Policy ID:
- Create a test PDF: `POLIZA_TEST_001.pdf` with any insurance policy text
- Use Policy ID: `TEST_001`

## Troubleshooting

### "GEMINI_API_KEY not found"
- Verify `.env` file exists in project root
- Check API key is correct (no extra spaces)
- Restart Streamlit after creating/editing `.env`

### "No PDF files found in data/policies"
- Verify PDFs are in `data/policies/` directory
- Check file extensions are `.pdf` (lowercase)
- Verify file permissions

### "No relevant sections found for policy"
- Verify Policy ID matches filename
- Try reindexing: Click "🔄 Reindexar (Sobrescribir)"
- Check PDF contains readable text (not just images)
- Verify the policy actually contains relevant information

### "Error generating report"
- Check API key is valid and has quota available
- Verify internet connection (needed for Gemini API)
- Check field notes are not empty
- Review error message in Streamlit interface

### Report quality issues
- Provide more detailed field notes
- Ensure policy PDFs contain comprehensive coverage information
- Adjust query context to focus on specific policy sections
- Consider providing more specific damage descriptions

## Advanced Usage

### Using the FastAPI Server

Instead of Streamlit UI, you can use the API:

1. **Start the server**:
   ```bash
   python3 main.py
   ```

2. **Generate report via API**:
   ```bash
   curl -X POST "http://localhost:8000/api/generate-report" \
     -H "Content-Type: application/json" \
     -d '{
       "field_notes": "El asegurado reportó daños...",
       "policy_id": "12345",
       "claim_id": "SIN-2024-001"
     }'
   ```

### WhatsApp Webhook (Future)

The `/webhook` endpoint is ready for Meta WhatsApp Cloud API integration. See `main.py` for details.

## Next Development Steps

1. **Add more policies** to improve coverage
2. **Fine-tune prompts** in `engine/generator.py` for better Spanish output
3. **Adjust chunking** in `engine/rag_engine.py` if search results are not relevant
4. **Customize PDF formatting** in `engine/pdf_exporter.py`
5. **Add error handling** and validation for specific use cases

## Support

- Check `README.md` for full documentation
- Review code comments in `engine/` modules
- Check logs in Streamlit terminal for detailed errors
