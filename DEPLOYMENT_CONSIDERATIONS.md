# Deployment Considerations for Streamlit Cloud

## ⚠️ Critical Issues for Deployment

### 1. **ChromaDB Persistence** ❌
**Problem:**
- Streamlit Cloud has an **ephemeral file system**
- Files in `data/chroma_db/` are **wiped on each deployment**
- ChromaDB data will be **lost** unless stored externally

**Impact:**
- Users will need to re-index all documents after each deployment
- Auto-initialization will work, but ChromaDB will be empty
- Not ideal for production

**Solutions:**

#### Option A: External Storage (Recommended for Production)
- Use **cloud storage** (S3, Google Cloud Storage, etc.)
- Store ChromaDB in cloud bucket
- Mount/download on app startup
- **Pros**: Persistent, scalable
- **Cons**: More complex setup, potential costs

#### Option B: Include in Git (Not Recommended)
- Commit ChromaDB to repository
- **Pros**: Simple
- **Cons**: Large files, slow deployments, not scalable

#### Option C: Re-index on Startup (Quick Fix)
- Auto-index documents on first run
- Check if ChromaDB exists, if not, index automatically
- **Pros**: Works out of the box
- **Cons**: Slow first load, requires PDFs in repo

#### Option D: Accept Re-indexing (Current State)
- Users manually index after deployment
- **Pros**: Simple, no changes needed
- **Cons**: Poor UX, manual step required

---

### 2. **PDF File Storage** ❌
**Problem:**
- PDFs in `data/policies/` and `data/internal_protocol_coverage/` won't persist
- Need to be in repository or external storage

**Solutions:**

#### Option A: Include PDFs in Git
- Commit PDFs to repository
- **Pros**: Simple, works immediately
- **Cons**: Large repository size, not ideal for many files

#### Option B: External Storage
- Store PDFs in cloud storage
- Download on startup or on-demand
- **Pros**: Scalable, no repo bloat
- **Cons**: More complex, potential costs

#### Option C: User Upload (Future Enhancement)
- Allow users to upload PDFs via UI
- Store in session or temporary storage
- **Pros**: Flexible, no repo management
- **Cons**: Data lost on session end, not persistent

---

### 3. **Environment Variables** ✅
**Status: Works Fine**
- Set `GEMINI_API_KEY` in Streamlit Cloud secrets
- Access via `os.getenv("GEMINI_API_KEY")`
- No changes needed

---

### 4. **Auto-Initialization** ✅
**Status: Will Work**
- `@st.cache_resource` works in deployment
- Session state persists during session
- Engine will initialize automatically
- **BUT**: ChromaDB will be empty unless using external storage

---

### 5. **Session State** ✅
**Status: Works Fine**
- Each user gets their own session
- State persists during session
- Lost on session timeout/refresh

---

## Recommended Deployment Strategy

### For Quick Deployment (MVP/Testing)

**Approach: Hybrid - Git + Auto-Index**

1. **Include PDFs in Git** (small number of files)
   - Commit essential policies/protocols to repo
   - Keep repo size manageable (<100MB)

2. **Auto-Index on First Run**
   - Check if ChromaDB exists
   - If not, automatically index all PDFs
   - Show progress indicator

3. **Accept Re-indexing After Deployments**
   - Document that users need to re-index after updates
   - Or auto-index on startup if ChromaDB missing

**Code Changes Needed:**
```python
# In app.py or rag_engine.py
def auto_index_if_needed(rag_engine):
    """Auto-index if ChromaDB is empty."""
    all_docs = rag_engine.get_all_indexed_documents()
    if not all_docs:
        # Check if PDFs exist
        if has_pdfs():
            # Auto-index
            rag_engine.index_documents(...)
```

**Pros:**
- ✅ Works out of the box
- ✅ No external dependencies
- ✅ Simple deployment

**Cons:**
- ⚠️ Slow first load (indexing)
- ⚠️ Re-indexing needed after deployments
- ⚠️ Limited scalability

---

### For Production Deployment

**Approach: External Storage**

1. **Use Cloud Storage for ChromaDB**
   - AWS S3, Google Cloud Storage, or similar
   - Download ChromaDB on startup
   - Upload updates periodically

2. **Use Cloud Storage for PDFs**
   - Store PDFs in cloud bucket
   - Download on-demand or cache locally
   - Allow admin uploads via UI

3. **Implement Caching Strategy**
   - Cache ChromaDB locally during session
   - Sync with cloud storage periodically
   - Handle conflicts gracefully

**Code Changes Needed:**
```python
# New module: engine/storage.py
class CloudStorage:
    def download_chromadb(self):
        """Download ChromaDB from cloud storage."""
        pass
    
    def upload_chromadb(self):
        """Upload ChromaDB to cloud storage."""
        pass
    
    def sync_pdfs(self):
        """Sync PDFs from cloud storage."""
        pass
```

**Pros:**
- ✅ Persistent data
- ✅ Scalable
- ✅ Professional solution

**Cons:**
- ⚠️ More complex setup
- ⚠️ Requires cloud storage account
- ⚠️ Potential costs

---

## Implementation Plan for Quick Deployment

### Phase 1: Make It Deployment-Ready (Current Plan)

**What Works:**
- ✅ Auto-initialization (will work)
- ✅ Template system (will work)
- ✅ Environment variables (will work)

**What Needs Adjustment:**
- ⚠️ Add auto-indexing on first run
- ⚠️ Handle empty ChromaDB gracefully
- ⚠️ Include PDFs in Git (or document upload process)

### Phase 2: Add Auto-Indexing

**Changes:**
1. Check if ChromaDB has documents on startup
2. If empty and PDFs exist, auto-index
3. Show progress indicator
4. Cache indexing status

**Code:**
```python
@st.cache_resource
def get_rag_engine():
    engine = RAGEngine(...)
    
    # Auto-index if needed
    if not engine.get_all_indexed_documents():
        if check_pdfs_exist():
            with st.spinner("Indexando documentos por primera vez..."):
                engine.index_documents(...)
    
    return engine
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] Set `GEMINI_API_KEY` in Streamlit Cloud secrets
- [ ] Include essential PDFs in repository (or set up external storage)
- [ ] Test auto-initialization locally
- [ ] Test auto-indexing locally
- [ ] Verify `requirements.txt` is complete

### Deployment Steps
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables
4. Deploy
5. Test first run (should auto-index)

### Post-Deployment
- [ ] Verify auto-initialization works
- [ ] Verify auto-indexing works (if implemented)
- [ ] Test document selection
- [ ] Test report generation
- [ ] Monitor for errors

---

## Current State Assessment

### ✅ Will Work Out of the Box:
- Auto-initialization (engine creation)
- Template system
- Environment variables
- Session state
- UI components

### ⚠️ Needs Adjustment:
- ChromaDB persistence (will be empty)
- PDF file access (need to be in repo or external)
- First-time indexing (manual or auto)

### ❌ Won't Work Without Changes:
- Persistent ChromaDB across deployments
- PDFs not in repository
- Automatic data persistence

---

## Recommendation

**For MVP/Testing:**
1. ✅ Implement auto-initialization (current plan)
2. ✅ Implement template system (current plan)
3. ✅ Add auto-indexing on first run
4. ✅ Include essential PDFs in Git
5. ✅ Document re-indexing process

**For Production:**
1. Implement cloud storage integration
2. Add admin UI for PDF management
3. Implement ChromaDB sync
4. Add monitoring and error handling

---

## Quick Fix: Auto-Index on Startup

Add this to the auto-initialization plan:

```python
# In app.py
@st.cache_resource
def get_rag_engine():
    """Get or create RAG engine with auto-indexing."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    engine = RAGEngine(...)
    
    # Auto-index if ChromaDB is empty
    if not engine.get_all_indexed_documents():
        # Check if PDFs exist
        policies_exist = list(Path("data/policies").glob("*.pdf"))
        protocols_exist = list(Path("data/internal_protocol_coverage").glob("*.pdf"))
        
        if policies_exist or protocols_exist:
            # Auto-index (silently or with indicator)
            engine.index_documents(
                index_policies=bool(policies_exist),
                index_protocols=bool(protocols_exist),
            )
    
    return engine
```

This makes it work "out of the box" for deployment, assuming PDFs are in the repo.

---

## Summary

**Will it work out of the box?**
- **Partially**: Auto-init and templates will work
- **But**: ChromaDB will be empty, needs indexing
- **Solution**: Add auto-indexing on first run + include PDFs in Git

**Best approach for deployment:**
1. Include essential PDFs in repository
2. Add auto-indexing on startup if ChromaDB empty
3. Accept that re-indexing happens after deployments
4. For production, migrate to cloud storage later
