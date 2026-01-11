# Plan: Flexible Document Selection System

## Overview
Transform the system from single-policy selection to multi-document selection, allowing users to choose which policies and internal protocols are relevant for each report.

## Current State Analysis

### Current Architecture
- **Single source**: Only indexes `data/policies/`
- **Single selection**: User selects one Policy ID
- **Metadata**: Stores `policy_id`, `source`, `file_path`
- **Search**: Filters by single `policy_id`

### New Requirements
- **Multiple sources**: Index both `data/policies/` and `data/internal_protocol_coverage/`
- **Multi-selection**: User selects multiple documents (policies + protocols)
- **Document types**: Distinguish between "póliza" and "protocolo"
- **Flexible search**: Search across selected documents only

---

## Implementation Plan

### Phase 1: Update RAG Engine (`engine/rag_engine.py`)

#### 1.1 Update `__init__` method
- Add `protocols_dir` parameter (default: `"data/internal_protocol_coverage"`)
- Keep `policies_dir` for backward compatibility
- Store both directories as instance variables

#### 1.2 Update `index_policies` method → Rename to `index_documents`
- **New method name**: `index_documents(overwrite: bool = False)`
- **Process both directories**:
  - Index all PDFs from `policies_dir`
  - Index all PDFs from `protocols_dir`
- **Enhanced metadata**:
  ```python
  {
      "document_id": "POLIZA_HOGAR_GLOBAL" or "21._Lluvia_y_nieve",
      "document_type": "póliza" or "protocolo",
      "source": "filename.pdf",
      "file_path": "full/path/to/file.pdf",
      "source_dir": "policies" or "internal_protocol_coverage"
  }
  ```
- **Document ID extraction**:
  - Policies: Use existing `extract_policy_id_from_filename()` logic
  - Protocols: Extract from filename (remove extension, clean up)

#### 1.3 New method: `get_all_indexed_documents()`
- Returns list of all indexed documents with metadata
- Format:
  ```python
  [
      {
          "document_id": "POLIZA_HOGAR_GLOBAL",
          "document_type": "póliza",
          "display_name": "POLIZA_HOGAR_GLOBAL",
          "source": "POLIZA_HOGAR_GLOBAL.pdf"
      },
      {
          "document_id": "21._Lluvia_y_nieve",
          "document_type": "protocolo",
          "display_name": "21. Lluvia y nieve - Daños en bienes continente",
          "source": "21._Lluvia_y_nieve._Danos_en_bienes_continente.pdf"
      }
  ]
  ```

#### 1.4 Update `search_by_policy_id` → Rename to `search_by_document_ids`
- **New method**: `search_by_document_ids(query: str, document_ids: List[str], k: int = 5)`
- **Parameters**:
  - `query`: Search query text
  - `document_ids`: List of document IDs to search within
  - `k`: Number of results per document (or total?)
- **Filtering**: Filter results to only include chunks from selected documents
- **Return**: Same format as before, but from multiple documents

#### 1.5 Update `get_policy_context` → Rename to `get_documents_context`
- **New method**: `get_documents_context(document_ids: List[str], query: str, max_chunks: int = 10)`
- **Parameters**: List of document IDs instead of single policy_id
- **Logic**: Search across all selected documents and combine results
- **Formatting**: Include document type and name in context sections

#### 1.6 Backward compatibility
- Keep `get_indexed_policy_ids()` for existing UI code
- Keep `search_by_policy_id()` as wrapper that calls new method
- Deprecate gradually

---

### Phase 2: Update Report Generator (`engine/generator.py`)

#### 2.1 Update `generate_report` method
- **Change parameter**: `policy_id: str` → `document_ids: List[str]`
- **Update RAG call**: Use `get_documents_context()` instead of `get_policy_context()`
- **Update prompt**: Reference "selected documents" instead of "policy"
- **Keep backward compatibility**: Accept `policy_id` and convert to list

#### 2.2 Update `generate_report_dict` method
- Accept `document_ids: List[str]` instead of `policy_id: str`
- Store `document_ids` in returned dictionary
- Update metadata accordingly

---

### Phase 3: Update Streamlit UI (`app.py`)

#### 3.1 Document Selection Section
- **Replace Policy ID dropdown** with **Multi-select Document Picker**
- **Layout**:
  ```
  ┌─────────────────────────────────────────┐
  │ 📚 Documentos Relevantes                │
  │                                         │
  │ [ ] POLIZA_HOGAR_GLOBAL (Póliza)       │
  │ [ ] POLIZA_HOGAR_BASICO (Póliza)        │
  │ [ ] 21. Lluvia y nieve (Protocolo)     │
  │ [ ] 22. Lluvia - Falta mantenimiento   │
  │                                         │
  │ [Buscar documentos...]                  │
  └─────────────────────────────────────────┘
  ```

#### 3.2 UI Components
- **Multi-select widget**: Use `st.multiselect()` or custom checkbox list
- **Grouping**: Show policies and protocols in separate sections
- **Search/Filter**: Add search box to filter document list
- **Document info**: Show document type badge (Póliza/Protocolo)
- **Validation**: Require at least one document selected

#### 3.3 Document Display Format
- **Policies**: Show as "POLIZA_HOGAR_GLOBAL" (Póliza)
- **Protocols**: Show cleaned name "21. Lluvia y nieve - Daños en bienes continente" (Protocolo)
- **Icons**: Use 📄 for policies, 📋 for protocols

#### 3.4 Update Form Flow
1. User selects multiple documents
2. User enters field notes
3. System searches across selected documents
4. Generates report using context from all selected documents

---

### Phase 4: Update Indexing UI

#### 4.1 Sidebar Updates
- **Separate indexing buttons**:
  - "📥 Indexar Pólizas" (policies only)
  - "📋 Indexar Protocolos" (protocols only)
  - "🔄 Indexar Todo" (both)
- **Status display**: Show count of indexed policies and protocols
- **Reindex options**: Separate reindex for each type

#### 4.2 Indexing Status
- Display: "5 pólizas indexadas, 20 protocolos indexados"
- Show last indexing time
- Show document count per type

---

### Phase 5: Enhanced Metadata & Context

#### 5.1 Context Formatting in Reports
When generating context from multiple documents:
```
[Póliza: POLIZA_HOGAR_GLOBAL]
Section content here...

[Protocolo: 21. Lluvia y nieve]
Section content here...
```

#### 5.2 Report Generation Prompt
Update to reference "selected documents" instead of "policy":
- "Based on the following selected documents: [list]"
- "Compare damages with relevant clauses from selected policies and protocols"

---

## Data Structure Changes

### Metadata Schema (ChromaDB)
```python
{
    "document_id": str,           # Unique identifier (filename without extension)
    "document_type": str,         # "póliza" or "protocolo"
    "source": str,                # Original filename
    "file_path": str,            # Full path to file
    "source_dir": str            # "policies" or "internal_protocol_coverage"
}
```

### Document List Format
```python
{
    "document_id": "POLIZA_HOGAR_GLOBAL",
    "document_type": "póliza",
    "display_name": "POLIZA_HOGAR_GLOBAL",
    "source": "POLIZA_HOGAR_GLOBAL.pdf",
    "source_dir": "policies"
}
```

---

## Migration Strategy

### Step 1: Add New Functionality (Non-Breaking)
- Add new methods alongside existing ones
- Keep old methods working
- New UI uses new methods

### Step 2: Update Indexing
- Reindex all documents with new metadata structure
- Both old and new metadata fields during transition

### Step 3: Update UI Gradually
- Add document selection UI
- Keep policy selection as fallback
- Migrate users to new UI

### Step 4: Deprecate Old Methods
- Mark old methods as deprecated
- Remove after migration period

---

## File Structure Changes

```
data/
├── policies/                    # Existing (no change)
│   └── POLIZA_*.pdf
├── internal_protocol_coverage/  # New (already exists)
│   └── *.pdf
└── chroma_db/                   # Updated metadata structure
```

---

## UI Mockup

### Main Form Section
```
┌─────────────────────────────────────────────────────┐
│ 📝 Generar Informe Pericial                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│ 📚 Documentos Relevantes (Selecciona uno o más)    │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 🔍 Buscar documentos...                        │ │
│ ├─────────────────────────────────────────────────┤ │
│ │ 📄 PÓLIZAS                                      │ │
│ │ ☑ POLIZA_HOGAR_GLOBAL                          │ │
│ │ ☐ POLIZA_HOGAR_BASICO                          │ │
│ │ ☐ POLIZA_HOGAR_OPTIMA                           │ │
│ ├─────────────────────────────────────────────────┤ │
│ │ 📋 PROTOCOLOS INTERNOS                          │ │
│ │ ☑ 21. Lluvia y nieve - Daños en bienes        │ │
│ │ ☐ 22. Lluvia - Falta de mantenimiento          │ │
│ │ ☐ 32. Filtraciones terrazas comunitarias       │ │
│ └─────────────────────────────────────────────────┘ │
│                                                     │
│ ID de Siniestro: [________________]                 │
│                                                     │
│ Notas de Campo:                                    │
│ [________________________________]                 │
│ [________________________________]                 │
│                                                     │
│ [🚀 Generar Informe]                               │
└─────────────────────────────────────────────────────┘
```

---

## Implementation Order

1. **Phase 1**: Update RAG Engine (backend changes)
   - Add protocols_dir support
   - Update indexing to handle both types
   - Add new search methods
   - Test with existing functionality

2. **Phase 2**: Update Generator (minimal changes)
   - Update to accept document_ids list
   - Update prompts

3. **Phase 3**: Update UI (frontend changes)
   - Add document selection widget
   - Update form flow
   - Add search/filter functionality

4. **Phase 4**: Polish & Testing
   - Test with multiple document combinations
   - Verify context quality
   - Update documentation

---

## Benefits

1. **Flexibility**: Users choose exactly which documents are relevant
2. **Better Context**: Reports can reference both policies and internal protocols
3. **Scalability**: Easy to add more document types in future
4. **User Control**: Perito has full control over document selection
5. **Better Reports**: More comprehensive analysis with multiple sources

---

## Considerations

1. **Performance**: Searching across multiple documents may be slower
   - Solution: Limit chunks per document, optimize queries

2. **Context Length**: Multiple documents = more context tokens
   - Solution: Smart chunking, prioritize most relevant chunks

3. **UI Complexity**: More complex than single selection
   - Solution: Good grouping, search, and clear labels

4. **Backward Compatibility**: Existing workflows should still work
   - Solution: Keep old methods, gradual migration

---

## Testing Checklist

- [ ] Index both policies and protocols
- [ ] Select single policy (backward compatibility)
- [ ] Select multiple policies
- [ ] Select policies + protocols
- [ ] Search across selected documents
- [ ] Generate report with multiple documents
- [ ] Verify context includes all selected documents
- [ ] Test with empty selection (validation)
- [ ] Test document search/filter functionality
- [ ] Verify metadata structure in ChromaDB

---

## Next Steps

1. Review and approve this plan
2. Start with Phase 1 (RAG Engine updates)
3. Test incrementally
4. Move to Phase 2 and 3
5. Final testing and deployment
