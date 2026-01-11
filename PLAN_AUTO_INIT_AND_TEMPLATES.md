# Plan: Auto-Initialization & Report Templates

## Issue 1: RAG Initialization & Indexing

### Current Problem
- Users must manually click "🔄 Inicializar Motor RAG" button
- In deployment, this step is required every time
- ChromaDB data persists, but the Python objects need initialization
- Manual indexing required for new PDFs

### Solution: Auto-Initialization

#### Approach 1: Auto-Initialize on App Load (Recommended)
**How it works:**
- Initialize RAG engine automatically when the app starts
- Check if ChromaDB exists and load it
- No user action required
- If initialization fails, show error but don't block UI

**Implementation:**
1. Move `initialize_engine()` call to app startup (before main UI)
2. Use `@st.cache_resource` or session state to persist engine
3. Check if ChromaDB exists - if yes, auto-load
4. Remove manual "Inicializar Motor RAG" button (or make it optional/advanced)

**Benefits:**
- ✅ Zero user friction
- ✅ Works well in deployment
- ✅ Engine ready immediately
- ✅ ChromaDB persists across sessions

**Code Changes:**
```python
# In app.py, at module level or in main()
@st.cache_resource
def get_rag_engine():
    """Get or create RAG engine (cached)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return RAGEngine(...)

# Auto-initialize
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = get_rag_engine()
    if st.session_state.rag_engine:
        st.session_state.generator = ReportGenerator(...)
```

#### Approach 2: Lazy Initialization
**How it works:**
- Initialize only when first needed (e.g., when user tries to select documents)
- Show loading spinner on first use
- Cache in session state after first initialization

**Benefits:**
- ✅ Faster initial load
- ✅ Only initializes if user actually uses the feature

**Drawbacks:**
- ⚠️ First use has delay
- ⚠️ More complex error handling

#### Recommended: Approach 1 (Auto-Initialize)
- Better UX (no waiting on first use)
- Simpler code
- Standard pattern for Streamlit apps

---

### Incremental Indexing

#### Current State
- Manual indexing via buttons
- Can index policies, protocols, or both
- Overwrite option available

#### Enhancement: Smart Indexing
**Add automatic detection of new files:**

1. **Check for new files on startup** (optional):
   - Compare file list with indexed documents
   - Show notification: "X new files detected, click to index"
   - Don't auto-index (user control)

2. **Incremental indexing by default**:
   - Current `index_documents(overwrite=False)` already does this
   - Only indexes new files not already in ChromaDB
   - Keep this behavior

3. **File watcher** (advanced, optional):
   - Watch directories for new PDFs
   - Auto-index when new file detected
   - Could be overkill for this use case

**Recommended:**
- Keep current incremental indexing (it already works)
- Add "Check for new files" button that shows what's new
- Don't auto-index (user should control when to index)

---

## Issue 2: Report Templates

### Current State
- Fixed 5-section structure:
  1. IDENTIFICACIÓN
  2. ANTECEDENTES
  3. ANÁLISIS DE CAUSALIDAD
  4. ANÁLISIS DE COBERTURA
  5. TASACIÓN Y PROPUESTA

### User's Example Template
- Simpler 3-section structure:
  1. CAUSA DEL SINIESTRO
  2. DAÑOS
  3. CONCLUSIÓN

### Solution: Template System

#### Architecture

**1. Template Definition Structure**
```python
# templates.py or engine/templates.py
TEMPLATES = {
    "completo": {
        "name": "Informe Completo (5 secciones)",
        "description": "Estructura completa con análisis detallado",
        "sections": [
            "IDENTIFICACIÓN",
            "ANTECEDENTES",
            "ANÁLISIS DE CAUSALIDAD",
            "ANÁLISIS DE COBERTURA",
            "TASACIÓN Y PROPUESTA"
        ],
        "prompt_template": """
        Generate report with sections:
        1. IDENTIFICACIÓN...
        2. ANTECEDENTES...
        ...
        """
    },
    "simplificado": {
        "name": "Informe Simplificado (3 secciones)",
        "description": "Estructura concisa para casos simples",
        "sections": [
            "CAUSA DEL SINIESTRO",
            "DAÑOS",
            "CONCLUSIÓN"
        ],
        "prompt_template": """
        Generate report with sections:
        1. CAUSA DEL SINIESTRO...
        2. DAÑOS...
        3. CONCLUSIÓN...
        """
    }
}
```

**2. Update ReportGenerator**
- Add `template_id` parameter to `generate_report()`
- Load template from dictionary
- Use template's prompt structure
- Keep system prompt generic (applies to all templates)

**3. UI Changes**
- Add template selector in form (dropdown/radio)
- Show template description
- Preview template structure
- Default to "completo" (current structure)

**4. Template Storage**
- Option A: Hardcoded in Python file (simple, fast)
- Option B: JSON/YAML file (easier to edit)
- Option C: Database (overkill for now)

**Recommended: Option A (Python dict)**
- Simple to implement
- Easy to version control
- Fast access
- Can migrate to file later if needed

---

### Implementation Plan

#### Phase 1: Auto-Initialization
1. ✅ Create `get_rag_engine()` cached function
2. ✅ Auto-initialize in `main()` before UI
3. ✅ Remove manual init button (or make it "Reinicializar")
4. ✅ Handle errors gracefully
5. ✅ Test with existing ChromaDB

#### Phase 2: Template System
1. ✅ Create `engine/templates.py` with template definitions
2. ✅ Update `ReportGenerator` to accept `template_id`
3. ✅ Update prompt generation to use selected template
4. ✅ Add template selector in UI
5. ✅ Test both templates

#### Phase 3: Enhanced Indexing (Optional)
1. ✅ Add "Check for new files" functionality
2. ✅ Show comparison of indexed vs available files
3. ✅ Keep incremental indexing as default

---

### File Structure Changes

```
engine/
├── __init__.py
├── rag_engine.py
├── generator.py
├── pdf_exporter.py
└── templates.py          # NEW: Template definitions

app.py                    # Updated with auto-init
```

---

### Template Example Implementation

**Template Definition:**
```python
# engine/templates.py
TEMPLATES = {
    "completo": {
        "name": "Informe Completo",
        "sections": [
            "IDENTIFICACIÓN",
            "ANTECEDENTES", 
            "ANÁLISIS DE CAUSALIDAD",
            "ANÁLISIS DE COBERTURA",
            "TASACIÓN Y PROPUESTA"
        ],
        "prompt_section": """
        Generate a comprehensive insurance adjuster report with:
        
        1. IDENTIFICACIÓN (Identification)
           - Policy details, Claim ID, Insured party, Dates
        
        2. ANTECEDENTES (Background)
           - Summary of incident and damages
        
        3. ANÁLISIS DE CAUSALIDAD (Causality Analysis)
           - Technical "Nexo Causal" evaluation
        
        4. ANÁLISIS DE COBERTURA (Coverage Analysis)
           - Comparison with policy clauses
        
        5. TASACIÓN Y PROPUESTA (Valuation and Proposal)
           - Economic estimation and verdict
        """
    },
    "simplificado": {
        "name": "Informe Simplificado",
        "sections": [
            "CAUSA DEL SINIESTRO",
            "DAÑOS",
            "CONCLUSIÓN"
        ],
        "prompt_section": """
        Generate a concise insurance adjuster report with:
        
        1. CAUSA DEL SINIESTRO (Cause of the Claim)
           - Visit details, location, insured party
           - Description of what happened
           - Technical findings and verification
        
        2. DAÑOS (Damages)
           - Detailed description of all damages observed
           - Affected areas and items
           - Extent of damage
        
        3. CONCLUSIÓN (Conclusion)
           - Coverage assessment
           - Final verdict (has coverage / no coverage)
           - Brief justification
        """
    }
}
```

**Generator Update:**
```python
def generate_report(
    self,
    field_notes: str,
    document_ids: List[str],
    template_id: str = "completo",  # NEW
    claim_id: Optional[str] = None,
    query_context: Optional[str] = None,
) -> str:
    # Load template
    template = TEMPLATES.get(template_id, TEMPLATES["completo"])
    
    # Use template's prompt structure
    user_prompt = f"""
    {template["prompt_section"]}
    
    SELECTED DOCUMENTS: {', '.join(selected_doc_names)}
    RELEVANT SECTIONS: {documents_context}
    FIELD NOTES: {field_notes}
    """
```

**UI Update:**
```python
# In form
template_selection = st.selectbox(
    "📋 Plantilla de Informe",
    options=list(TEMPLATES.keys()),
    format_func=lambda x: TEMPLATES[x]["name"],
    help="Selecciona la estructura del informe"
)

# Show template description
st.caption(TEMPLATES[template_selection]["description"])
```

---

### Benefits

**Auto-Initialization:**
- ✅ Zero user friction
- ✅ Better deployment experience
- ✅ ChromaDB persists, engine auto-loads
- ✅ Can still manually reindex new PDFs

**Templates:**
- ✅ Flexibility for different report types
- ✅ User can choose appropriate structure
- ✅ Easy to add more templates later
- ✅ Maintains quality with structured prompts

---

### Migration Notes

**For Auto-Init:**
- Existing ChromaDB will auto-load
- No data migration needed
- Users won't notice change (just better UX)

**For Templates:**
- Default to "completo" (current structure)
- Existing workflows continue to work
- New template is optional enhancement

---

### Testing Checklist

**Auto-Init:**
- [ ] App starts without manual initialization
- [ ] ChromaDB loads existing data
- [ ] New session still works
- [ ] Error handling if API key missing
- [ ] Error handling if ChromaDB corrupted

**Templates:**
- [ ] Both templates generate valid reports
- [ ] Template selector works in UI
- [ ] Reports match template structure
- [ ] Default template works (backward compat)
- [ ] Can add more templates easily

---

## Summary

### Recommended Implementation Order:
1. **Auto-Initialization** (Quick win, better UX)
2. **Template System** (Adds flexibility)
3. **Enhanced Indexing** (Nice to have, optional)

### Estimated Effort:
- Auto-Init: ~30 minutes
- Templates: ~1-2 hours
- Enhanced Indexing: ~1 hour (optional)

### Risk Assessment:
- **Low Risk**:** Auto-init and templates are additive features
- **No Breaking Changes**: Existing functionality preserved
- **Easy Rollback**: Can revert if issues

---

**Ready to implement?** Let me know if you want any changes to this plan!
