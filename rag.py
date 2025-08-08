from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain.text_splitter import CharacterTextSplitter
import google.generativeai as genai
import time
import streamlit as st # Import the streamlit library

class RAGSystem:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.text_chunks = []
        
        # Access the API key using st.secrets
        api_key = st.secrets["GOOGLE_API_KEY"]
        if not api_key:
            raise ValueError("GOOGLE_API_KEY secret not set in Streamlit")
        genai.configure(api_key=api_key)
        self.gemini_model = genai.GenerativeModel("gemini-1.5-flash")

    def index_documents(self, texts):
        text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        self.text_chunks = text_splitter.split_text("\n".join(texts))
        embeddings = self.model.encode(self.text_chunks)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def query(self, question, k=3):
        query_embedding = self.model.encode([question])[0]
        distances, indices = self.index.search(np.array([query_embedding]), k)
        retrieved_chunks = [self.text_chunks[i] for i in indices[0]]
        return retrieved_chunks

    def generate_response(self, question, retrieved_chunks):
        context = "\n".join(retrieved_chunks)
        prompt = f"Contexto:\n{context}\n\nPregunta: {question}\nRespuesta:"
        for attempt in range(3):
            try:
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config={
                        "max_output_tokens": 500,
                        "temperature": 0.7
                    }
                )
                return response.text.strip()
            except Exception as e:
                if "rate limit" in str(e).lower():
                    time.sleep(2 ** attempt)
                    continue
                return f"Error calling Gemini API: {str(e)}"
        return "Error: API rate limit exceeded"
        