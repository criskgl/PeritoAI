"""Report Generator using LLM with Spanish output."""

import os
from typing import Optional, Dict, Any, List

from langchain_google_genai import ChatGoogleGenerativeAI

# Try new import structure first, fallback to old structure for compatibility
try:
    from langchain_core.messages import HumanMessage, SystemMessage
except ImportError:
    # Fallback for older LangChain versions
    from langchain.schema import HumanMessage, SystemMessage

from .rag_engine import RAGEngine
from .templates import get_template


class ReportGenerator:
    """Generates insurance adjuster reports in Spanish using RAG and LLM."""

    def __init__(
        self,
        rag_engine: RAGEngine,
        api_key: Optional[str] = None,
        model_name: str = "gemini-2.5-flash-lite",
    ):
        """
        Initialize Report Generator.

        Args:
            rag_engine: Initialized RAGEngine instance
            api_key: Google Gemini API key
            model_name: LLM model name (default: 'gemini-2.5-flash-lite')
                       Other options: 'gemini-2.5-flash', 'gemini-1.5-pro', etc.
        """
        self.rag_engine = rag_engine
        self.model_name = model_name

        # Initialize LangChain Gemini chat model
        # Using gemini-2.5-flash-lite: optimized for cost-efficiency and high throughput
        # Supports up to 1M input tokens and 65K output tokens
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.3,  # Lower temperature for more consistent output
            google_api_key=api_key or os.getenv("GEMINI_API_KEY"),
        )

        # System prompt in English that instructs AI to write in Professional Spanish
        self.system_prompt = """You are an expert insurance adjuster (perito de seguros) in Spain. 
Your task is to generate professional insurance adjuster reports (Informes Periciales) in Spanish, 
following Spanish insurance industry standards and regulations.

Key requirements:
1. Write all content in Professional Spanish using insurance industry terminology
2. Use proper Spanish insurance jargon such as:
   - "siniestro indemnizable" (indemnifiable claim)
   - "daños estéticos" (aesthetic damages)
   - "valor a nuevo" (replacement value)
   - "nexo causal" (causal link)
   - "cobertura" (coverage)
   - "póliza" (policy)
   - "asegurado" (insured)
   - "tomador" (policyholder)
   - "prima" (premium)
   - "franquicia" (deductible)
   - "peritaje" (expert appraisal)
   - "tasación" (valuation/assessment)
   - "daños materiales" (material damages)
   - "bien asegurado" (insured property)

3. Maintain a formal, professional, and objective tone
4. Structure the report according to Spanish insurance standards
5. Base all analysis on the provided policy documents and field notes
6. Be precise and technical in your assessment
7. Always justify your conclusions with evidence from the policy and field observations"""

    def generate_report(
        self,
        field_notes: str,
        document_ids: List[str],
        template_id: str = "completo",
        claim_id: Optional[str] = None,
        query_context: Optional[str] = None,
        perito_info: Optional[Dict[str, str]] = None,
        parsed_claim_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Generate a complete insurance adjuster report in Spanish.

        Args:
            field_notes: Adjuster's field notes/story from the visit
            document_ids: List of Document IDs to search for relevant sections
            template_id: Template ID to use for report structure (default: "completo")
            claim_id: Optional claim ID to include in the report
            query_context: Optional specific query to find relevant sections

        Returns:
            Complete insurance adjuster report in Spanish
        """
        if not document_ids:
            raise ValueError("document_ids must be provided and cannot be empty")

        # Load template
        template = get_template(template_id)

        # If no specific query, use field notes to find relevant sections
        if query_context is None:
            query_context = field_notes[:500]  # Use first 500 chars as query

        # Retrieve relevant context from selected documents using RAG
        documents_context = self.rag_engine.get_documents_context(
            document_ids=document_ids,
            query=query_context,
            max_chunks=10,
        )

        # Get document names for display
        all_docs = self.rag_engine.get_all_indexed_documents()
        doc_info = {doc["document_id"]: doc for doc in all_docs}
        selected_doc_names = [
            doc_info.get(doc_id, {}).get("display_name", doc_id) 
            for doc_id in document_ids
        ]

        # Build perito information string
        perito_info_text = ""
        if perito_info:
            perito_parts = []
            if perito_info.get("nombre"):
                perito_parts.append(f"Nombre: {perito_info['nombre']}")
            if perito_info.get("colegiado"):
                perito_parts.append(f"Colegiado: {perito_info['colegiado']}")
            if perito_info.get("empresa"):
                perito_parts.append(f"Empresa/Gabinete: {perito_info['empresa']}")
            if perito_parts:
                perito_info_text = "\n".join(perito_parts)

        # Build claim information from parsed data
        claim_info_text = ""
        if parsed_claim_data:
            claim_parts = []
            if parsed_claim_data.get("policy_number"):
                claim_parts.append(f"Póliza: {parsed_claim_data['policy_number']}")
            if parsed_claim_data.get("insured_name"):
                claim_parts.append(f"Asegurado: {parsed_claim_data['insured_name']}")
            if parsed_claim_data.get("dni"):
                claim_parts.append(f"DNI: {parsed_claim_data['dni']}")
            if parsed_claim_data.get("address"):
                claim_parts.append(f"Domicilio: {parsed_claim_data['address']}")
            if parsed_claim_data.get("cause"):
                claim_parts.append(f"Causa: {parsed_claim_data['cause']}")
            if claim_parts:
                claim_info_text = "\n".join(claim_parts)

        # Construct the user prompt with template structure
        user_prompt = f"""Generate an insurance adjuster report (Informe Pericial) based on the following information:

SELECTED DOCUMENTS:
{', '.join(selected_doc_names)}

CLAIM INFORMATION:
{claim_info_text if claim_info_text else f"Claim ID: {claim_id if claim_id else 'N/A'}"}

PERITO INFORMATION:
{perito_info_text if perito_info_text else 'Not provided'}

RELEVANT DOCUMENT SECTIONS:
{documents_context}

FIELD NOTES FROM ADJUSTER VISIT:
{field_notes}

{template['prompt_section']}

IMPORTANT: 
- Write everything in Professional Spanish
- Use proper insurance terminology throughout
- Be objective and technical
- Base all conclusions on the provided document clauses and field observations
- Reference specific documents when citing coverage or protocols
- Ensure the report follows Spanish insurance industry standards
- Follow the exact structure specified above"""

        # Generate report using LLM
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_prompt),
        ]

        try:
            response = self.llm.invoke(messages)
            report = response.content
            return report
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error message if model not found
            if "NOT_FOUND" in error_msg or "404" in error_msg:
                raise Exception(
                    f"Model '{self.model_name}' not found or not available with your API version.\n"
                    f"Error details: {error_msg}\n"
                    f"Please try one of these models: 'gemini-2.5-flash-lite', 'gemini-2.5-flash', 'gemini-1.5-flash'\n"
                    f"Or check available models at: https://ai.google.dev/gemini-api/docs/models/gemini"
                )
            raise Exception(f"Error generating report: {error_msg}")

    def generate_report_dict(
        self,
        field_notes: str,
        document_ids: List[str],
        template_id: str = "completo",
        claim_id: Optional[str] = None,
        query_context: Optional[str] = None,
        perito_info: Optional[Dict[str, str]] = None,
        parsed_claim_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate report and return as structured dictionary.

        Args:
            field_notes: Adjuster's field notes/story from the visit
            document_ids: List of Document IDs to search for relevant sections
            template_id: Template ID to use for report structure (default: "completo")
            claim_id: Optional claim ID to include in the report
            query_context: Optional specific query to find relevant sections

        Returns:
            Dictionary containing report sections and metadata
        """
        report_text = self.generate_report(
            field_notes=field_notes,
            document_ids=document_ids,
            template_id=template_id,
            claim_id=claim_id,
            query_context=query_context,
            perito_info=perito_info,
            parsed_claim_data=parsed_claim_data,
        )

        return {
            "report_text": report_text,
            "document_ids": document_ids,
            "template_id": template_id,
            "claim_id": claim_id,
            "field_notes": field_notes,
            "perito_info": perito_info,
            "parsed_claim_data": parsed_claim_data,
        }
