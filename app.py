import streamlit as st
import os
from document_processor import extract_text
from rag import RAGSystem
from jinja2 import Environment, FileSystemLoader

# Configuración inicial
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicializar sistema RAG
rag = RAGSystem()

# Interfaz de Streamlit
st.title("Sistema para Peritos - Prototipo")
st.header("Carga de Documentos")

# Carga de múltiples archivos
uploaded_files = st.file_uploader("Sube documentos (PDF, TXT, DOCX, JPG, PNG)", accept_multiple_files=True, type=["pdf", "txt", "docx", "jpg", "png"])

if uploaded_files:
    texts = []
    for uploaded_file in uploaded_files:
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        text = extract_text(file_path)
        texts.append(text)
        st.write(f"Procesado: {uploaded_file.name}")
    
    # Indexar documentos
    rag.index_documents(texts)
    st.success("Documentos indexados correctamente.")

# Consultas
st.header("Consulta y Generación de Informes")
question = st.text_input("Haz una pregunta sobre los documentos:")
if question:
    retrieved_chunks = rag.query(question)
    response = rag.generate_response(question, retrieved_chunks)
    st.write("**Respuesta generada:**")
    st.write(response)

# Generación de informe
st.header("Generar Informe")
if st.button("Generar informe preliminar"):
    # Placeholder: generar informe basado en plantilla
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("informe_template.jinja2")
    report_content = template.render(data={"titulo": "Informe Preliminar", "contenido": response})
    
    # Mostrar informe editable
    edited_report = st.text_area("Edita el informe:", value=report_content, height=300)
    
    # Descarga del informe final
    if st.button("Descargar Informe Final"):
        with open("informe_final.txt", "w", encoding="utf-8") as f:
            f.write(edited_report)
        st.download_button("Descargar", data=edited_report, file_name="informe_final.txt")
