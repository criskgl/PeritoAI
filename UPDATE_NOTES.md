# Update Notes - Model Change

## Changes Made

### 1. Updated Default Model to `gemini-2.5-flash-lite`
- Changed from `gemini-1.5-pro` → `gemini-2.5-flash-lite`
- This model is optimized for cost-efficiency and high throughput
- Better compatibility with current API versions

### 2. Removed Deprecated `google.generativeai` Imports
- Removed direct `google.generativeai` imports
- LangChain's `langchain-google-genai` handles all API interactions
- Note: You may still see deprecation warnings from LangChain's internal dependencies

### 3. Improved Error Messages
- Added better error handling for model not found errors
- Suggests alternative models if current one fails
- Provides helpful links to check available models

## Testing

After these changes:
1. **Restart Streamlit** if it's running
2. **Try generating a report** with Policy ID `POLIZA_HOGAR_GLOBAL`
3. If you still get errors, check:
   - Your API key is valid and has access to the model
   - Your API quota hasn't been exceeded
   - You're using the correct API version

## Alternative Models to Try

If `gemini-2.5-flash-lite` doesn't work, try these in order:

1. `gemini-2.5-flash` - Similar but slightly different characteristics
2. `gemini-1.5-flash` - Older but widely available
3. `gemini-1.5-pro` - More powerful but may require specific access

To change the model, edit `engine/generator.py` line 25:
```python
model_name: str = "gemini-2.5-flash-lite",  # Change this line
```

## Model Specifications

### gemini-2.5-flash-lite
- **Input tokens**: Up to 1,048,576
- **Output tokens**: Up to 65,536
- **Optimized for**: Cost-efficiency and high throughput
- **Best for**: Production applications with large context needs

See more: https://ai.google.dev/gemini-api/docs/models/gemini
