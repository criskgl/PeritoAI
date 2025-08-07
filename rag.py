from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain.text_splitter import CharacterTextSplitter

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.text_chunks = []

    def index_documents(self, texts):
        # Dividir textos en fragmentos
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.text_chunks = text_splitter.split_text("\n".join(texts))
        
        # Generar embeddings
        embeddings = self.model.encode(self.text_chunks)
        
        # Crear índice FAISS
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def query(self, question, k=3):
        # Generar embedding de la pregunta
        query_embedding = self.model.encode([question])[0]
        
        # Buscar fragmentos relevantes
        distances, indices = self.index.search(np.array([query_embedding]), k)
        
        # Recuperar fragmentos
        retrieved_chunks = [self.text_chunks[i] for i in indices[0]]
        return retrieved_chunks

    def generate_response(self, question, retrieved_chunks):
        # Placeholder: integrar con Grok 3 (vía API) o modelo local
        context = "\n".join(retrieved_chunks)
        prompt = f"Contexto:\n{context}\n\nPregunta: {question}\nRespuesta:"
        # Aquí llamas a la API de Grok 3 (ver https://x.ai/api) o modelo local
        return f"Respuesta generada para: {question}\nContexto: {context[:200]}..."
