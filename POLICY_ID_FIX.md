# Policy ID Matching Fix

## Issue
Users were getting "No se encontraron secciones relevantes" warning even when Policy IDs should match.

## Root Cause
The `extract_policy_id_from_filename` function was removing the `POLIZA_` prefix, so:
- File: `POLIZA_HOGAR_GLOBAL.pdf` → Stored as: `HOGAR_GLOBAL`
- User enters: `POLIZA_HOGAR_GLOBAL` → Doesn't match!

## Solution

### 1. Updated Policy ID Extraction
- Now keeps the **full filename** (without extension) as Policy ID
- `POLIZA_HOGAR_GLOBAL.pdf` → Policy ID: `POLIZA_HOGAR_GLOBAL`
- This allows users to enter the full name they see in the filename

### 2. Flexible Matching
- Added case-insensitive matching
- Supports partial matches (e.g., `HOGAR_GLOBAL` will match `POLIZA_HOGAR_GLOBAL`)
- Handles variations in how users enter the Policy ID

### 3. Better Error Messages
- Shows available Policy IDs when search fails
- Provides helpful suggestions
- Makes it clear what Policy IDs are indexed

## How to Use

### Option 1: Use Full Filename (Recommended)
- File: `POLIZA_HOGAR_GLOBAL.pdf`
- Enter: `POLIZA_HOGAR_GLOBAL`

### Option 2: Use Partial Name
- File: `POLIZA_HOGAR_GLOBAL.pdf`
- Enter: `HOGAR_GLOBAL` (will also work due to flexible matching)

## Next Steps

1. **Reindex your policies** to update the stored Policy IDs:
   - In Streamlit UI, click "🔄 Reindexar (Sobrescribir)" in the sidebar
   - This will update all Policy IDs to use the full filename format

2. **Try generating a report again** with Policy ID: `POLIZA_HOGAR_GLOBAL`

## Available Policy IDs

After reindexing, you should see these Policy IDs:
- `POLIZA_HOGAR_ALQUILER_PROPIETARIO`
- `POLIZA_HOGAR_BASICO`
- `POLIZA_HOGAR_GLOBAL`
- `POLIZA_HOGAR_OPTIMA`
- `POLIZA_HOGAR_SEGUNDA_VIVIENDA`
