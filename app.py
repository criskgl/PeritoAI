"""Streamlit UI for PeritoAI - Insurance Adjuster Report Generator."""

import os
import sys
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add engine module to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.rag_engine import RAGEngine
from engine.generator import ReportGenerator
from engine.pdf_exporter import ReportPDFExporter
from engine.templates import get_available_templates, get_template
from engine.claim_parser import ClaimDataParser


# Page configuration
st.set_page_config(
    page_title="PeritoAI - Generador de Informes Periciales",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = None
if "generator" not in st.session_state:
    st.session_state.generator = None
if "document_search_term" not in st.session_state:
    st.session_state.document_search_term = ""
if "perito_info" not in st.session_state:
    st.session_state.perito_info = {
        "nombre": "",
        "colegiado": "",
        "empresa": "",
    }
if "parsed_claim_data" not in st.session_state:
    st.session_state.parsed_claim_data = None
if "auto_suggested_docs" not in st.session_state:
    st.session_state.auto_suggested_docs = []
if "selected_document_ids" not in st.session_state:
    st.session_state.selected_document_ids = []


@st.cache_resource
def get_rag_engine():
    """Get or create RAG engine (cached across reruns)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    try:
        return RAGEngine(
            policies_dir="data/policies",
            protocols_dir="data/internal_protocol_coverage",
            chroma_db_dir="data/chroma_db",
            api_key=api_key,
        )
    except Exception as e:
        st.error(f"Error initializing RAG engine: {str(e)}")
        return None


@st.cache_resource
def get_report_generator(_rag_engine):
    """Get or create Report Generator (cached across reruns)."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    
    try:
        return ReportGenerator(
            rag_engine=_rag_engine,
            api_key=api_key,
        )
    except Exception as e:
        st.error(f"Error initializing report generator: {str(e)}")
        return None


def initialize_engine():
    """Auto-initialize RAG engine and generator."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False

    try:
        if st.session_state.rag_engine is None:
            st.session_state.rag_engine = get_rag_engine()
            if st.session_state.rag_engine:
                st.session_state.generator = get_report_generator(st.session_state.rag_engine)
        return st.session_state.rag_engine is not None and st.session_state.generator is not None
    except Exception as e:
        st.error(f"Error initializing engine: {str(e)}")
        return False


def main():
    """Main Streamlit application."""
    st.title("📋 PeritoAI - Generador de Informes Periciales")
    st.markdown("**Sistema automatizado para la generación de informes periciales de seguros**")

    # Auto-initialize engine
    if not initialize_engine():
        st.error("⚠️ Error al inicializar el motor RAG. Verifica que GEMINI_API_KEY esté configurado.")
        st.stop()

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Show initialization status
        if st.session_state.rag_engine and st.session_state.generator:
            st.success("✅ Motor RAG inicializado")
        
        # Optional: Reinitialize button (for advanced users)
        with st.expander("🔧 Opciones Avanzadas"):
            if st.button("🔄 Reinicializar Motor RAG"):
                # Clear cache and reinitialize
                get_rag_engine.clear()
                get_report_generator.clear()
                st.session_state.rag_engine = None
                st.session_state.generator = None
                st.rerun()

        st.divider()

        # Index documents section
        st.subheader("📚 Índice de Documentos")
        
        # Show indexing status
        if st.session_state.rag_engine:
            all_docs = st.session_state.rag_engine.get_all_indexed_documents()
            policies_count = len([d for d in all_docs if d["document_type"] == "póliza"])
            protocols_count = len([d for d in all_docs if d["document_type"] == "protocolo"])
            st.caption(f"📊 {policies_count} pólizas, {protocols_count} protocolos indexados")
        
        # Index options
        col_idx1, col_idx2 = st.columns(2)
        
        with col_idx1:
            if st.button("📥 Indexar Pólizas", use_container_width=True):
                if st.session_state.rag_engine is None:
                    st.error("Error: Motor RAG no inicializado")
                else:
                    with st.spinner("Indexando pólizas..."):
                        try:
                            st.session_state.rag_engine.index_documents(
                                overwrite=False,
                                index_policies=True,
                                index_protocols=False,
                            )
                            st.success("Pólizas indexadas correctamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al indexar: {str(e)}")
        
        with col_idx2:
            if st.button("📋 Indexar Protocolos", use_container_width=True):
                if st.session_state.rag_engine is None:
                    st.error("Error: Motor RAG no inicializado")
                else:
                    with st.spinner("Indexando protocolos..."):
                        try:
                            st.session_state.rag_engine.index_documents(
                                overwrite=False,
                                index_policies=False,
                                index_protocols=True,
                            )
                            st.success("Protocolos indexados correctamente")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error al indexar: {str(e)}")
        
        if st.button("🔄 Indexar Todo", use_container_width=True):
            if st.session_state.rag_engine is None:
                st.error("Error: Motor RAG no inicializado")
            else:
                with st.spinner("Indexando todos los documentos..."):
                    try:
                        st.session_state.rag_engine.index_documents(
                            overwrite=False,
                            index_policies=True,
                            index_protocols=True,
                        )
                        st.success("Todos los documentos indexados correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al indexar: {str(e)}")
        
        if st.button("🗑️ Reindexar Todo (Sobrescribir)", use_container_width=True):
            if st.session_state.rag_engine is None:
                st.error("Error: Motor RAG no inicializado")
            else:
                with st.spinner("Reindexando todos los documentos..."):
                    try:
                        st.session_state.rag_engine.index_documents(
                            overwrite=True,
                            index_policies=True,
                            index_protocols=True,
                        )
                        st.success("Todos los documentos reindexados correctamente")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al reindexar: {str(e)}")

        st.divider()

        # Instructions
        st.subheader("📖 Instrucciones")
        st.markdown("""
        1. **Inicializar Motor RAG**: Carga el motor de búsqueda vectorial
        2. **Indexar Documentos**: Procesa PDFs de pólizas y/o protocolos
        3. **Seleccionar Documentos**: Elige los documentos relevantes para el informe
        4. **Completar Formulario**: Ingresa las notas de campo
        5. **Generar Informe**: El sistema creará el informe en español
        6. **Descargar PDF**: Descarga el informe generado
        """)

    # Engine should already be initialized, but double-check
    if st.session_state.rag_engine is None or st.session_state.generator is None:
        st.error("⚠️ Error: Motor RAG no inicializado. Por favor, reinicia la aplicación.")
        st.stop()

    # Claim Data Input Section
    st.subheader("📥 Datos del Siniestro")
    
    # Initialize auto_suggested_doc_ids at the start
    auto_suggested_doc_ids = st.session_state.get("auto_suggested_docs", [])
    claim_data_input = st.text_area(
        "Pega los datos del siniestro (Póliza, DNI, Descripción, Causa, etc.)",
        placeholder="""Póliza: 515360
DNI: 30177374V
Asegurado: RAFAEL NUÑEZ LAMO
Descripción del siniestro: ROTURA DE TUBERIA...
Causa: ROTURA DE TUBERIA EMPOTRADA""",
        height=150,
        help="Pega aquí toda la información del siniestro. El sistema extraerá automáticamente los datos relevantes.",
    )

    # Parse claim data and auto-suggest documents
    claim_parser = ClaimDataParser()
    parsed_data = None
    auto_suggested_doc_ids = []

    if claim_data_input.strip():
        # Parse claim data
        parsed_data = claim_parser.parse_claim_data(claim_data_input)
        st.session_state.parsed_claim_data = parsed_data

        # Show parsed data preview
        with st.expander("👁️ Datos Extraídos", expanded=False):
            if parsed_data.get("policy_number"):
                st.write(f"**Póliza:** {parsed_data['policy_number']}")
            if parsed_data.get("dni"):
                st.write(f"**DNI:** {parsed_data['dni']}")
            if parsed_data.get("insured_name"):
                st.write(f"**Asegurado:** {parsed_data['insured_name']}")
            if parsed_data.get("cause"):
                st.write(f"**Causa:** {parsed_data['cause']}")
            if parsed_data.get("claim_description"):
                st.write(f"**Descripción:** {parsed_data['claim_description'][:200]}...")

        # Auto-suggest documents based on semantic search
        if parsed_data.get("search_query"):
            with st.spinner("🔍 Buscando documentos relevantes..."):
                try:
                    # Search all documents with the claim description/cause
                    all_docs = st.session_state.rag_engine.get_all_indexed_documents()
                    if all_docs:
                        all_doc_ids = [doc["document_id"] for doc in all_docs]
                        
                        # Search across all documents
                        search_results = st.session_state.rag_engine.search_by_document_ids(
                            query=parsed_data["search_query"],
                            document_ids=all_doc_ids,
                            k=10,  # Get top 10 most relevant
                        )

                        # Get unique document IDs from results, ranked by relevance
                        doc_scores = {}
                        for result in search_results:
                            doc_id = result["metadata"].get("document_id")
                            if doc_id:
                                score = result.get("score", 999)
                                # Lower score is better, so track best (lowest) score per doc
                                if doc_id not in doc_scores or score < doc_scores[doc_id]:
                                    doc_scores[doc_id] = score

                        # Sort by score and get top documents
                        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1])
                        auto_suggested_doc_ids = [doc_id for doc_id, _ in sorted_docs[:8]]  # Top 8
                        st.session_state.auto_suggested_docs = auto_suggested_doc_ids

                        if auto_suggested_doc_ids:
                            # Get document names for display
                            doc_info_map = {doc["document_id"]: doc for doc in all_docs}
                            suggested_doc_names = [
                                doc_info_map.get(doc_id, {}).get("display_name", doc_id)
                                for doc_id in auto_suggested_doc_ids
                            ]
                            
                            # Build the "basados en" text
                            basados_en = parsed_data.get('cause') or parsed_data.get('claim_description', '')[:100] or 'descripción del siniestro'
                            if len(basados_en) > 100:
                                basados_en = basados_en[:100] + "..."
                            
                            st.success(f"✓ Se encontraron {len(auto_suggested_doc_ids)} documentos relevantes basados en: **{basados_en}**")
                            
                            # Show document names
                            with st.expander(f"📋 Ver documentos sugeridos ({len(suggested_doc_names)})", expanded=True):
                                for doc_name in suggested_doc_names:
                                    st.markdown(f"  • {doc_name}")
                except Exception as e:
                    st.warning(f"No se pudieron sugerir documentos automáticamente: {str(e)}")

    st.divider()

    # Document Selection Section (outside form for reactive search) - Collapsible
    with st.expander("📚 Seleccionar Documentos Manualmente (Opcional)", expanded=False):
        st.markdown("Selecciona o deselecciona documentos (pólizas y/o protocolos) que consideras relevantes para este informe:")
        
        # Get all indexed documents
        all_documents = st.session_state.rag_engine.get_all_indexed_documents()
        
        if all_documents:
            # Separate documents by type
            policies = [doc for doc in all_documents if doc.get("document_type") == "póliza"]
            protocols = [doc for doc in all_documents if doc.get("document_type") == "protocolo"]
            
            # Debug info if no pólizas found (helps diagnose indexing issues)
            if not policies and all_documents:
                all_types = set(doc.get("document_type", "unknown") for doc in all_documents)
                st.warning(f"⚠️ No se encontraron pólizas indexadas. Tipos de documentos encontrados: {all_types}")
                st.info(f"ℹ️ Total documentos indexados: {len(all_documents)}. Asegúrate de haber indexado las pólizas desde la barra lateral.")
            
            # Search/filter input (reactive - updates as you type)
            search_term = st.text_input(
                "🔍 Buscar documentos...",
                value=st.session_state.document_search_term,
                placeholder="Escribe para filtrar la lista en tiempo real",
                help="Filtra documentos por nombre mientras escribes",
                key="document_search_input",
            )
            
            # Update session state
            st.session_state.document_search_term = search_term
            
            # Filter documents based on search (fuzzy matching)
            if search_term:
                search_lower = search_term.lower().strip()
                # Split search term into words for better matching
                search_words = search_lower.split()
                
                def matches_search(doc):
                    """Check if document matches search (fuzzy)."""
                    display_lower = doc["display_name"].lower()
                    doc_id_lower = doc["document_id"].lower()
                    
                    # Check if all search words appear in display name or document ID
                    return all(
                        word in display_lower or word in doc_id_lower
                        for word in search_words
                    )
                
                policies = [doc for doc in policies if matches_search(doc)]
                protocols = [doc for doc in protocols if matches_search(doc)]
            
            # Create two columns for policies and protocols
            col_pol, col_prot = st.columns(2)
            
            with col_pol:
                st.markdown("### 📄 Pólizas")
                if policies:
                    for doc in policies:
                        doc_id = doc["document_id"]
                        display_name = doc["display_name"]
                        checkbox_key = f"doc_{doc_id}"
                        
                        # Check if this document was auto-suggested
                        is_auto_suggested = doc_id in auto_suggested_doc_ids
                        default_value = is_auto_suggested
                        
                        checkbox_label = display_name
                        if is_auto_suggested:
                            checkbox_label = f"🤖 {display_name}"
                        
                        checked = st.checkbox(
                            checkbox_label,
                            value=default_value,
                            key=checkbox_key,
                            help=f"ID: {doc_id}" + (" (Sugerido automáticamente)" if is_auto_suggested else "")
                        )
                else:
                    if search_term:
                        st.info("No se encontraron pólizas con ese término de búsqueda.")
                    else:
                        st.info("No hay pólizas indexadas.")
            
            with col_prot:
                st.markdown("### 📋 Protocolos Internos")
                if protocols:
                    for doc in protocols:
                        doc_id = doc["document_id"]
                        display_name = doc["display_name"]
                        checkbox_key = f"doc_{doc_id}"
                        
                        # Check if this document was auto-suggested
                        is_auto_suggested = doc_id in auto_suggested_doc_ids
                        default_value = is_auto_suggested
                        
                        checkbox_label = display_name
                        if is_auto_suggested:
                            checkbox_label = f"🤖 {display_name}"
                        
                        checked = st.checkbox(
                            checkbox_label,
                            value=default_value,
                            key=checkbox_key,
                            help=f"ID: {doc_id}" + (" (Sugerido automáticamente)" if is_auto_suggested else "")
                        )
                else:
                    if search_term:
                        st.info("No se encontraron protocolos con ese término de búsqueda.")
                    else:
                        st.info("No hay protocolos indexados.")
            
            # Show selection summary (collect from checkboxes)
            manual_selected_docs = []
            for doc in all_documents:
                checkbox_key = f"doc_{doc['document_id']}"
                if st.session_state.get(checkbox_key, False):
                    manual_selected_docs.append(doc["document_id"])
            
            if manual_selected_docs:
                st.success(f"✓ **{len(manual_selected_docs)}** documento(s) seleccionado(s) manualmente")
                with st.expander("Ver documentos seleccionados"):
                    for doc_id in manual_selected_docs:
                        doc_info = next((d for d in all_documents if d["document_id"] == doc_id), None)
                        if doc_info:
                            doc_type_icon = "📄" if doc_info["document_type"] == "póliza" else "📋"
                            st.write(f"{doc_type_icon} {doc_info['display_name']}")
                
                # Update selected_document_ids with manual selection
                st.session_state.selected_document_ids = manual_selected_docs
            else:
                # If no manual selection, use auto-suggested
                if auto_suggested_doc_ids:
                    st.session_state.selected_document_ids = auto_suggested_doc_ids.copy()
                else:
                    st.session_state.selected_document_ids = []
        else:
            st.info("ℹ️ No hay documentos indexados. Por favor, indexa las pólizas y protocolos desde la barra lateral primero.")
            st.session_state.selected_document_ids = []
    
    # Get selected_document_ids from session state (use auto-suggested if available)
    selected_document_ids = st.session_state.get("selected_document_ids", [])
    if not selected_document_ids and auto_suggested_doc_ids:
        selected_document_ids = auto_suggested_doc_ids.copy()
        st.session_state.selected_document_ids = selected_document_ids
    
    st.divider()
    
    # Form for report generation
    with st.form("report_form"):
        # Template selection - locked to "simplificado" for now
        # TODO: Re-enable template selection UI in future
        selected_template_id = "simplificado"  # Default template
        
        # Show template info (locked)
        selected_template = get_template(selected_template_id)
        st.info(f"📋 **Plantilla:** {selected_template['name']} - {selected_template['description']}")
        
        # Show template preview with sections
        sections = selected_template.get("sections", [])
        if sections:
            st.markdown("**📋 Estructura del informe:**")
            # Display sections in a nice format
            sections_text = " → ".join([f"**{sec}**" for sec in sections])
            st.markdown(sections_text)
        
        st.divider()
        
        # Perito Information Section
        st.subheader("👤 Información del Perito")
        
        col_per1, col_per2 = st.columns(2)
        with col_per1:
            perito_nombre = st.text_input(
                "Nombre del Perito",
                value=st.session_state.perito_info.get("nombre", ""),
                placeholder="Ej: Juan Pérez García",
                help="Nombre completo del perito",
            )
        
        with col_per2:
            perito_colegiado = st.text_input(
                "Número de Colegiado (Opcional)",
                value=st.session_state.perito_info.get("colegiado", ""),
                placeholder="Ej: 12345",
                help="Número de colegiado si aplica",
            )
        
        perito_empresa = st.text_input(
            "Empresa/Gabinete",
            value=st.session_state.perito_info.get("empresa", ""),
            placeholder="Ej: Gabinete Pericial XYZ",
            help="Nombre de la empresa o gabinete pericial",
        )
        
        # Update session state
        st.session_state.perito_info = {
            "nombre": perito_nombre,
            "colegiado": perito_colegiado,
            "empresa": perito_empresa,
        }
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Pre-fill claim_id from parsed data if available
            claim_id_default = ""
            if parsed_data and parsed_data.get("policy_number"):
                claim_id_default = parsed_data.get("policy_number")
            
            claim_id = st.text_input(
                "ID de Siniestro (Opcional)",
                value=claim_id_default,
                placeholder="Ej: SIN-2024-001",
                help="Identificador único del siniestro",
            )

        with col2:
            pass  # Reserved for future fields

        # Pre-fill field notes from parsed claim description if available
        field_notes_default = ""
        if parsed_data and parsed_data.get("claim_description"):
            field_notes_default = parsed_data.get("claim_description", "")
        
        field_notes = st.text_area(
            "Notas de Campo del Perito",
            value=field_notes_default,
            placeholder="Describe los hallazgos de la inspección, daños observados, circunstancias del siniestro, etc.",
            height=300,
            help="Relato detallado de la visita del perito y observaciones realizadas",
        )

        query_context = st.text_input(
            "Contexto de Búsqueda (Opcional)",
            placeholder="Palabras clave para buscar en los documentos (dejar vacío para usar las notas de campo)",
            help="Texto específico para buscar secciones relevantes en los documentos seleccionados",
        )

        submit_button = st.form_submit_button("🚀 Generar Informe", use_container_width=True)

        if submit_button:
            # Validation - get selected documents from checkboxes (already collected above)
            if not selected_document_ids:
                st.error("⚠️ Por favor, selecciona al menos un documento relevante")
                st.stop()

            if not field_notes:
                st.error("⚠️ Por favor, ingresa las notas de campo")
                st.stop()

            # Generate report
            with st.spinner("🔍 Buscando información relevante en los documentos seleccionados..."):
                try:
                    # Search for relevant sections in selected documents
                    search_results = st.session_state.rag_engine.search_by_document_ids(
                        query=query_context or field_notes[:500],
                        document_ids=selected_document_ids,
                        k=5,
                    )

                    if not search_results:
                        st.warning(
                            f"⚠️ No se encontraron secciones relevantes en los documentos seleccionados. "
                            "Intenta con un contexto de búsqueda más específico o selecciona otros documentos."
                        )
                    else:
                        st.success(f"✓ Se encontraron {len(search_results)} secciones relevantes en {len(selected_document_ids)} documento(s)")
                except Exception as e:
                    st.error(f"Error al buscar en los documentos: {str(e)}")

            with st.spinner("✍️ Generando informe pericial en español..."):
                try:
                    # Generate report
                    report_dict = st.session_state.generator.generate_report_dict(
                        field_notes=field_notes,
                        document_ids=selected_document_ids,
                        template_id=selected_template_id,
                        claim_id=claim_id if claim_id else None,
                        query_context=query_context if query_context else None,
                        perito_info=st.session_state.perito_info if any(st.session_state.perito_info.values()) else None,
                        parsed_claim_data=st.session_state.parsed_claim_data,
                    )

                    # Store in session state
                    st.session_state.last_report = report_dict
                    st.session_state.report_generated = True

                    st.success("✅ Informe generado correctamente!")

                except Exception as e:
                    st.error(f"❌ Error al generar el informe: {str(e)}")
                    st.exception(e)

    # Display generated report
    if st.session_state.get("report_generated", False) and st.session_state.get("last_report"):
        st.divider()
        st.header("📄 Informe Generado")

        report_dict = st.session_state.last_report
        report_text = report_dict.get("report_text", "")

        # Display report
        st.text_area(
            "Contenido del Informe",
            value=report_text,
            height=500,
            label_visibility="collapsed",
        )

        # Download buttons
        col1, col2 = st.columns(2)

        with col1:
            # Download as text
            st.download_button(
                label="📥 Descargar como Texto (.txt)",
                data=report_text,
                file_name=f"informe_{'_'.join(report_dict.get('document_ids', ['unknown']))}_{report_dict.get('claim_id', 'unknown')}.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with col2:
            # Generate and download PDF
            if st.button("📄 Generar y Descargar PDF", use_container_width=True):
                with st.spinner("Generando PDF..."):
                    try:
                        exporter = ReportPDFExporter()
                        pdf_path = exporter.export_from_dict(report_dict)

                        # Read PDF file
                        with open(pdf_path, "rb") as pdf_file:
                            pdf_data = pdf_file.read()

                        st.download_button(
                            label="📥 Descargar PDF",
                            data=pdf_data,
                            file_name=Path(pdf_path).name,
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Error al generar PDF: {str(e)}")
                        st.exception(e)


if __name__ == "__main__":
    main()
