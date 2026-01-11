"""RAG Engine for PDF indexing and vector search."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any

import fitz  # PyMuPDF
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Try new import structure first, fallback to old structure for compatibility
try:
    from langchain_community.vectorstores import Chroma
except ImportError:
    # Fallback for older LangChain versions
    from langchain.vectorstores import Chroma


class RAGEngine:
    """Handles PDF processing, chunking, and vector search using ChromaDB."""

    def __init__(
        self,
        policies_dir: str = "data/policies",
        protocols_dir: str = "data/internal_protocol_coverage",
        chroma_db_dir: str = "data/chroma_db",
        embedding_model: str = "models/text-embedding-004",
        api_key: Optional[str] = None,
    ):
        """
        Initialize RAG Engine.

        Args:
            policies_dir: Directory containing policy PDFs
            protocols_dir: Directory containing internal protocol/coverage PDFs
            chroma_db_dir: Directory for ChromaDB persistence
            embedding_model: Embedding model name
            api_key: Google Gemini API key
        """
        self.policies_dir = Path(policies_dir)
        self.protocols_dir = Path(protocols_dir)
        self.chroma_db_dir = Path(chroma_db_dir)
        self.embedding_model = embedding_model

        # Initialize embeddings
        # GoogleGenerativeAIEmbeddings will use GEMINI_API_KEY from environment or api_key parameter
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model=embedding_model,
            google_api_key=api_key or os.getenv("GEMINI_API_KEY"),
        )

        # Initialize ChromaDB with persistent storage
        self.vectorstore = None
        self._initialize_vectorstore()

    def _initialize_vectorstore(self):
        """Initialize or load existing ChromaDB vectorstore."""
        # Ensure directory exists
        self.chroma_db_dir.mkdir(parents=True, exist_ok=True)

        # Try to load existing vectorstore, otherwise create new one
        try:
            self.vectorstore = Chroma(
                persist_directory=str(self.chroma_db_dir),
                embedding_function=self.embeddings,
            )
        except Exception:
            # Create new vectorstore if loading fails
            self.vectorstore = Chroma(
                persist_directory=str(self.chroma_db_dir),
                embedding_function=self.embeddings,
            )

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text content from a PDF file.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text content
        """
        doc = fitz.open(pdf_path)
        text_parts = []

        for page in doc:
            text_parts.append(page.get_text())

        doc.close()
        return "\n".join(text_parts)

    def extract_policy_id_from_filename(self, filename: str) -> str:
        """
        Extract Policy ID from filename.
        Returns the filename without extension as the Policy ID.
        This allows users to enter the full name (e.g., POLIZA_HOGAR_GLOBAL)
        or just the ID part (e.g., HOGAR_GLOBAL).

        Args:
            filename: PDF filename

        Returns:
            Policy ID string (full filename without extension)
        """
        # Return the full filename without extension as Policy ID
        # This allows flexible matching: users can enter full name or just ID part
        return Path(filename).stem

    def extract_document_id_from_filename(self, filename: str, document_type: str) -> str:
        """
        Extract Document ID from filename based on document type.

        Args:
            filename: PDF filename
            document_type: "póliza" or "protocolo"

        Returns:
            Document ID string
        """
        name = Path(filename).stem
        if document_type == "póliza":
            return name
        else:  # protocolo
            # For protocols, clean up the filename (remove numbers, underscores, etc.)
            # Keep it readable but use as ID
            return name

    def format_protocol_display_name(self, filename: str) -> str:
        """
        Format protocol filename into a readable display name.

        Args:
            filename: Protocol PDF filename

        Returns:
            Formatted display name
        """
        name = Path(filename).stem
        # Replace underscores with spaces
        name = name.replace("_", " ")
        # Clean up multiple spaces
        name = " ".join(name.split())
        # Try to extract meaningful parts (e.g., "21. Lluvia y nieve - Daños en bienes")
        return name

    def _index_directory(
        self,
        directory: Path,
        document_type: str,
        text_splitter: RecursiveCharacterTextSplitter,
        documents: list,
        metadatas: list,
    ) -> int:
        """
        Index all PDFs in a directory.

        Args:
            directory: Directory path to index
            document_type: "póliza" or "protocolo"
            text_splitter: Text splitter instance
            documents: List to append document chunks
            metadatas: List to append metadata

        Returns:
            Number of files processed
        """
        if not directory.exists():
            print(f"{document_type.capitalize()} directory {directory} does not exist. Creating it.")
            directory.mkdir(parents=True, exist_ok=True)
            return 0

        pdf_files = list(directory.glob("*.pdf"))
        if not pdf_files:
            print(f"No PDF files found in {directory}")
            return 0

        files_processed = 0
        for pdf_path in pdf_files:
            print(f"Processing {document_type}: {pdf_path.name}...")
            try:
                # Extract text
                text = self.extract_text_from_pdf(pdf_path)
                if not text.strip():
                    print(f"Warning: {pdf_path.name} appears to be empty or unreadable.")
                    continue

                # Extract Document ID from filename
                document_id = self.extract_document_id_from_filename(pdf_path.name, document_type)

                # Split text into chunks
                chunks = text_splitter.split_text(text)

                # Create metadata for each chunk
                for chunk in chunks:
                    documents.append(chunk)
                    metadatas.append({
                        "document_id": document_id,
                        "document_type": document_type,
                        "source": pdf_path.name,
                        "file_path": str(pdf_path),
                        "source_dir": "policies" if document_type == "póliza" else "internal_protocol_coverage",
                        # Keep policy_id for backward compatibility
                        "policy_id": document_id if document_type == "póliza" else None,
                    })

                files_processed += 1
            except Exception as e:
                print(f"Error processing {pdf_path.name}: {e}")
                continue

        return files_processed

    def index_policies(self, overwrite: bool = False):
        """
        Index all PDFs in the policies directory.
        (Kept for backward compatibility)

        Args:
            overwrite: If True, recreate the index from scratch
        """
        self.index_documents(overwrite=overwrite, index_policies=True, index_protocols=False)

    def index_documents(
        self,
        overwrite: bool = False,
        index_policies: bool = True,
        index_protocols: bool = True,
    ):
        """
        Index all PDFs from policies and/or protocols directories.

        Args:
            overwrite: If True, recreate the index from scratch
            index_policies: If True, index policies directory
            index_protocols: If True, index protocols directory
        """
        if overwrite:
            # Clear existing vectorstore
            self._initialize_vectorstore()

        # Text splitter configuration
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        documents = []
        metadatas = []

        policies_count = 0
        protocols_count = 0

        # Index policies
        if index_policies:
            policies_count = self._index_directory(
                self.policies_dir,
                "póliza",
                text_splitter,
                documents,
                metadatas,
            )

        # Index protocols
        if index_protocols:
            protocols_count = self._index_directory(
                self.protocols_dir,
                "protocolo",
                text_splitter,
                documents,
                metadatas,
            )

        if documents:
            # Add documents to vectorstore
            self.vectorstore.add_texts(texts=documents, metadatas=metadatas)
            total_chunks = len(documents)
            print(f"Successfully indexed:")
            if index_policies:
                print(f"  - {policies_count} pólizas")
            if index_protocols:
                print(f"  - {protocols_count} protocolos")
            print(f"  - Total: {total_chunks} chunks")
        else:
            print("No documents to index.")

    def get_indexed_policy_ids(self) -> List[str]:
        """
        Get list of all Policy IDs that are currently indexed.
        (Kept for backward compatibility)

        Returns:
            List of unique Policy IDs
        """
        all_docs = self.get_all_indexed_documents()
        return sorted([doc["document_id"] for doc in all_docs if doc["document_type"] == "póliza"])

    def get_all_indexed_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of all indexed documents (policies and protocols) with metadata.

        Returns:
            List of dictionaries with document information
        """
        if not self.vectorstore:
            return []
        
        try:
            # Try to access ChromaDB collection directly to get all metadata
            if hasattr(self.vectorstore, '_collection'):
                collection = self.vectorstore._collection
                all_items = collection.get()
                if all_items and 'metadatas' in all_items:
                    documents_map = {}
                    for metadata in all_items['metadatas']:
                        if metadata:
                            doc_id = metadata.get("document_id")
                            if doc_id:
                                # Store document info (use first occurrence)
                                if doc_id not in documents_map:
                                    doc_type = metadata.get("document_type", "póliza")
                                    source = metadata.get("source", "")
                                    
                                    # Format display name
                                    if doc_type == "protocolo":
                                        display_name = self.format_protocol_display_name(source)
                                    else:
                                        display_name = doc_id
                                    
                                    documents_map[doc_id] = {
                                        "document_id": doc_id,
                                        "document_type": doc_type,
                                        "display_name": display_name,
                                        "source": source,
                                        "source_dir": metadata.get("source_dir", ""),
                                    }
                    return list(documents_map.values())
            
            # Fallback: Use similarity search with multiple generic queries
            documents_map = {}
            generic_queries = ["", "póliza", "seguro", "cobertura", "cláusula", "protocolo"]
            for query in generic_queries:
                try:
                    docs = self.vectorstore.similarity_search(query, k=500)
                    for doc in docs:
                        doc_id = doc.metadata.get("document_id")
                        if doc_id and doc_id not in documents_map:
                            doc_type = doc.metadata.get("document_type", "póliza")
                            source = doc.metadata.get("source", "")
                            
                            # Format display name
                            if doc_type == "protocolo":
                                display_name = self.format_protocol_display_name(source)
                            else:
                                display_name = doc_id
                            
                            documents_map[doc_id] = {
                                "document_id": doc_id,
                                "document_type": doc_type,
                                "display_name": display_name,
                                "source": source,
                                "source_dir": doc.metadata.get("source_dir", ""),
                            }
                except Exception:
                    continue
            
            return list(documents_map.values())
        except Exception as e:
            print(f"Error getting indexed documents: {e}")
            return []

    def search_by_policy_id(
        self,
        query: str,
        policy_id: str,
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks filtered by Policy ID.
        Supports flexible matching: matches full Policy ID or partial matches.

        Args:
            query: Search query text
            policy_id: Policy ID to filter by (can be full name like 'POLIZA_HOGAR_GLOBAL' or partial)
            k: Number of results to return

        Returns:
            List of relevant document chunks with metadata
        """
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Please index policies first.")

        # Normalize policy_id for flexible matching (case-insensitive)
        policy_id_normalized = policy_id.upper().strip()
        
        # Get more results initially, then filter to ensure we have enough matches
        try:
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k * 3,  # Get more results for better filtering
            )
            # Manual filtering by policy_id with flexible matching
            filtered_results = []
            for doc, score in results:
                stored_policy_id = doc.metadata.get("policy_id", "").upper()
                # Match if exact match, or if stored ID contains the search term, or vice versa
                if (stored_policy_id == policy_id_normalized or 
                    policy_id_normalized in stored_policy_id or 
                    stored_policy_id in policy_id_normalized):
                    filtered_results.append((doc, score))
            
            # Limit to k results, sorted by score (lower is better)
            filtered_results.sort(key=lambda x: x[1])
            results = filtered_results[:k]
            
            if not results:
                # Try to get all indexed policy IDs for helpful error message
                all_policy_ids = self.get_indexed_policy_ids()
                print(f"Warning: No results found for policy_id='{policy_id}' after filtering")
                if all_policy_ids:
                    print(f"Available Policy IDs: {', '.join(all_policy_ids)}")
        except Exception as e:
            # Fallback: Unfiltered search with manual filtering
            print(f"Search failed: {e}. Trying fallback search...")
            results = self.vectorstore.similarity_search_with_score(query, k=k * 3)
            # Manual filtering with flexible matching
            policy_id_normalized = policy_id.upper().strip()
            results = [
                (doc, score)
                for doc, score in results
                if (doc.metadata.get("policy_id", "").upper() == policy_id_normalized or
                    policy_id_normalized in doc.metadata.get("policy_id", "").upper() or
                    doc.metadata.get("policy_id", "").upper() in policy_id_normalized)
            ][:k]

        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            })

        return formatted_results

    def search_by_document_ids(
        self,
        query: str,
        document_ids: List[str],
        k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks filtered by multiple Document IDs.

        Args:
            query: Search query text
            document_ids: List of Document IDs to filter by
            k: Number of results per document (approximate total will be k * len(document_ids))

        Returns:
            List of relevant document chunks with metadata
        """
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized. Please index documents first.")

        if not document_ids:
            return []

        # Normalize document IDs for flexible matching (case-insensitive)
        document_ids_normalized = [doc_id.upper().strip() for doc_id in document_ids]
        
        try:
            # Get more results to ensure we have enough from all selected documents
            results = self.vectorstore.similarity_search_with_score(
                query,
                k=k * len(document_ids) * 2,  # Get more results for better filtering
            )
            
            # Manual filtering by document_ids with flexible matching
            filtered_results = []
            for doc, score in results:
                stored_doc_id = doc.metadata.get("document_id", "").upper()
                # Match if stored ID matches any of the requested IDs
                matches = any(
                    stored_doc_id == doc_id_norm or 
                    doc_id_norm in stored_doc_id or 
                    stored_doc_id in doc_id_norm
                    for doc_id_norm in document_ids_normalized
                )
                if matches:
                    filtered_results.append((doc, score))
            
            # Limit to k results per document, sorted by score (lower is better)
            filtered_results.sort(key=lambda x: x[1])
            
            # Distribute results across documents (try to get k from each)
            results_by_doc = {}
            for doc, score in filtered_results:
                doc_id = doc.metadata.get("document_id", "")
                if doc_id not in results_by_doc:
                    results_by_doc[doc_id] = []
                if len(results_by_doc[doc_id]) < k:
                    results_by_doc[doc_id].append((doc, score))
            
            # Flatten and limit total results
            final_results = []
            for doc_id in document_ids_normalized:
                # Find matching stored doc_id
                for stored_doc_id, results_list in results_by_doc.items():
                    if (stored_doc_id.upper() == doc_id or 
                        doc_id in stored_doc_id.upper() or 
                        stored_doc_id.upper() in doc_id):
                        final_results.extend(results_list)
                        break
            
            # Sort by score and limit
            final_results.sort(key=lambda x: x[1])
            results = final_results[:k * len(document_ids)]
            
            if not results:
                all_doc_ids = [doc["document_id"] for doc in self.get_all_indexed_documents()]
                print(f"Warning: No results found for document_ids={document_ids} after filtering")
                print(f"Available Document IDs: {', '.join(all_doc_ids[:10])}...")
        except Exception as e:
            # Fallback: Unfiltered search with manual filtering
            print(f"Search failed: {e}. Trying fallback search...")
            results = self.vectorstore.similarity_search_with_score(query, k=k * len(document_ids) * 2)
            document_ids_normalized = [doc_id.upper().strip() for doc_id in document_ids]
            results = [
                (doc, score)
                for doc, score in results
                if any(
                    doc.metadata.get("document_id", "").upper() == doc_id_norm or
                    doc_id_norm in doc.metadata.get("document_id", "").upper() or
                    doc.metadata.get("document_id", "").upper() in doc_id_norm
                    for doc_id_norm in document_ids_normalized
                )
            ][:k * len(document_ids)]

        formatted_results = []
        for doc, score in results:
            formatted_results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": score,
            })

        return formatted_results

    def get_policy_context(self, policy_id: str, query: str, max_chunks: int = 10) -> str:
        """
        Get relevant policy context for a given query and Policy ID.
        (Kept for backward compatibility)

        Args:
            policy_id: Policy ID to search within
            query: Query to find relevant sections
            max_chunks: Maximum number of chunks to retrieve

        Returns:
            Formatted context string from relevant policy sections
        """
        return self.get_documents_context([policy_id], query, max_chunks)

    def get_documents_context(
        self,
        document_ids: List[str],
        query: str,
        max_chunks: int = 10,
    ) -> str:
        """
        Get relevant context from multiple selected documents.

        Args:
            document_ids: List of Document IDs to search within
            query: Query to find relevant sections
            max_chunks: Maximum number of chunks to retrieve per document

        Returns:
            Formatted context string from relevant document sections
        """
        if not document_ids:
            return "No documents selected."

        results = self.search_by_document_ids(query, document_ids, k=max_chunks)

        if not results:
            return f"No relevant sections found in selected documents: {', '.join(document_ids)}."

        # Group results by document
        results_by_doc = {}
        for result in results:
            doc_id = result['metadata'].get('document_id', 'Unknown')
            doc_type = result['metadata'].get('document_type', 'póliza')
            if doc_id not in results_by_doc:
                results_by_doc[doc_id] = {
                    'type': doc_type,
                    'results': []
                }
            results_by_doc[doc_id]['results'].append(result)

        context_parts = []
        for doc_id, doc_data in results_by_doc.items():
            doc_type_label = "Póliza" if doc_data['type'] == "póliza" else "Protocolo"
            context_parts.append(f"\n[{doc_type_label}: {doc_id}]")
            for i, result in enumerate(doc_data['results'], 1):
                context_parts.append(
                    f"  [Sección {i}]\n  {result['content']}\n"
                    f"  (Fuente: {result['metadata'].get('source', 'Unknown')})"
                )

        return "\n\n".join(context_parts)
