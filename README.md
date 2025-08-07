[200~# PeritoAI - Sistema para Peritos

**PeritoAI** is a prototype web application designed for peritos (experts) in Spain. It allows users to upload multiple document types (PDF, TXT, DOCX, JPG, PNG), process them using a Retrieval-Augmented Generation (RAG) system, answer queries based on the documents, and generate editable reports from customizable templates. Built with **Streamlit** for a user-friendly interface, this prototype is lightweight, modular, and designed for easy scalability to include features like authentication and Stripe payments in the future.

---

## Features

- **Multi-format Document Upload**: Supports PDF, TXT, DOCX, JPG, and PNG files.
- **Text Extraction**: Extracts text from documents using `PyPDF2` (PDF), `python-docx` (DOCX), `pytesseract` (images), and native reading (TXT).
- **RAG System**: Indexes documents with `sentence-transformers` and `FAISS` for efficient retrieval, enabling query-based responses and report generation.
- **Report Generation**: Creates editable reports based on Jinja2 templates, with options to review and download the final version.
- **Scalable Design**: Modular structure for future integration of authentication, Stripe payments, and cloud storage.

---

## Tech Stack

- **Frontend**: Streamlit
- **Backend**:
    - Document Processing: `PyPDF2`, `python-docx`, `pytesseract`, `Pillow`
    - RAG: `sentence-transformers`, `FAISS`, `langchain`
    - Templating: `Jinja2`
- **Language**: Python 3.8+
- **Future Integrations**: xAI Grok 3 API (see [xAI API](https://x.ai/api)), Stripe SDK, cloud storage (AWS S3/Google Cloud Storage)

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Tesseract OCR (for image processing): [Install Tesseract](https://github.com/tesseract-ocr/tesseract)
- Git (optional, for cloning the repository)

### Steps

1.  **Clone the Repository** (or download the code):
    ```bash
    git clone [https://github.com/your-username/peritoai.git](https://github.com/your-username/peritoai.git)
    cd peritoai
    ```
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set Up Tesseract**:
    - Install Tesseract OCR and ensure it’s added to your system PATH.
    - For Spanish OCR, ensure the `spa` language pack is installed (`tesseract --list-langs`).
5.  **Create Required Folders**:
    ```bash
    mkdir uploads vector_store templates
    ```
6.  **Add a Report Template**:
    - Create a file `templates/informe_template.jinja2` with the following content:
    ```jinja2
    # Informe Pericial

    **Título**: {{ data.titulo }}
    **Contenido**: {{ data.contenido }}
    **Fecha**: {{ data.fecha | default('07/08/2025') }}
    ```
7.  **Run the Application**:
    ```bash
    streamlit run app.py
    ```
    - Open your browser at `http://localhost:8501` to access the app.

---

## Usage

1.  **Upload Documents**:
    - Use the Streamlit interface to upload multiple files (PDF, TXT, DOCX, JPG, PNG).
    - Files are processed, and text is extracted and indexed for RAG.
2.  **Query Documents**:
    - Enter a question in the input field to retrieve relevant information from uploaded documents.
    - The RAG system returns a response based on the indexed content.
3.  **Generate and Edit Reports**:
    - Click "Generar informe preliminar" to create a report based on the template.
    - Edit the report in the provided text area.
    - Download the final report as a text file (future versions may support PDF/DOCX).

---

## Current Limitations

- **Language Model**: The prototype uses a placeholder for the language model in `rag.py`. For production, integrate with xAI’s Grok 3 API (see [xAI API](https://x.ai/api)) or a local model like LLaMA.
- **Report Formats**: Currently supports text-based reports. Future versions may include PDF export with `reportlab`.
- **Error Handling**: Basic error handling for document processing; needs enhancement for production.
- **Scalability**: Local file storage is used for simplicity. For production, consider cloud storage (AWS S3, Google Cloud Storage).

---

## Future Enhancements

- **Authentication**: Add user login with `streamlit-authenticator` or a FastAPI backend.
- **Payments**: Integrate Stripe for paid subscriptions (see [Stripe API](https://stripe.com/docs/api)).
- **Advanced Reports**: Support for complex templates and PDF/DOCX export.
- **Cloud Deployment**: Use Docker and AWS/GCP for scalable hosting.
- **Improved RAG**: Integrate Grok 3 for better query responses (details at [xAI API](https://x.ai/api)).

---

## Contributing

Contributions are welcome! Please:

1.  Fork the repository.
2.  Create a feature branch (`git checkout -b feature/your-feature`).
3.  Commit your changes (`git commit -m "Add your feature"`).
4.  Push to the branch (`git push origin feature/your-feature`).
5.  Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Contact

For questions or suggestions, contact [cris.kgl@gmail.com] or open an issue on GitHub.
