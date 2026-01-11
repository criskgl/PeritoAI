"""Report template definitions for different informe pericial structures."""

TEMPLATES = {
    "completo": {
        "name": "Informe Completo (5 secciones)",
        "description": "Estructura completa con análisis detallado de causalidad, cobertura y tasación",
        "sections": [
            "IDENTIFICACIÓN",
            "ANTECEDENTES",
            "ANÁLISIS DE CAUSALIDAD",
            "ANÁLISIS DE COBERTURA",
            "TASACIÓN Y PROPUESTA"
        ],
        "prompt_section": """Generate a comprehensive insurance adjuster report (Informe Pericial) with the following structure:

1. IDENTIFICACIÓN (Identification)
   - Policy details (póliza)
   - Claim ID (número de siniestro)
   - Insured party information (asegurado)
   - Date of incident (fecha del siniestro)
   - Date of inspection (fecha de inspección)

2. ANTECEDENTES (Background)
   - Summary of the incident based on field notes
   - Description of damages observed
   - Initial assessment from the adjuster's visit

3. ANÁLISIS DE CAUSALIDAD (Causality Analysis)
   - Technical "Nexo Causal" (causal link) analysis
   - Evaluation of whether the damages are related to covered causes
   - Assessment of cause-effect relationship
   - Technical justification based on findings

4. ANÁLISIS DE COBERTURA (Coverage Analysis)
   - Comparison between observed damages and relevant clauses from selected documents
   - Review of applicable coverage sections from policies and protocols
   - Assessment of exclusions and limitations
   - Determination of what is covered and what is not
   - Reference to specific clauses from selected documents

5. TASACIÓN Y PROPUESTA (Valuation and Proposal)
   - Economic estimation of damages (valoración económica)
   - Detailed breakdown of costs
   - Consideration of deductibles (franquicia) if applicable
   - Final verdict on claim eligibility (siniestro indemnizable or not)
   - Recommended settlement amount (importe propuesto)
   - Justification of the proposed amount"""
    },
    
    "simplificado": {
        "name": "Informe Simplificado (3 secciones)",
        "description": "Estructura concisa para casos simples: causa, daños y conclusión",
        "sections": [
            "CAUSA DEL SINIESTRO",
            "DAÑOS",
            "CONCLUSIÓN"
        ],
        "prompt_section": """Generate a concise insurance adjuster report (Informe Pericial) with the following structure:

1. CAUSA DEL SINIESTRO (Cause of the Claim)
   - Visit details: location, date, insured party information
   - Description of what happened based on field notes
   - Technical findings and verification during inspection
   - Details of the incident and circumstances
   - Any relevant observations about the cause

2. DAÑOS (Damages)
   - Detailed description of all damages observed
   - Affected areas and items
   - Extent and severity of damage
   - Specific locations and materials affected
   - Any damages to third parties if applicable

3. CONCLUSIÓN (Conclusion)
   - Coverage assessment based on selected documents
   - Reference to relevant policy clauses or protocols
   - Final verdict: whether the claim has coverage (TIENE COBERTURA) or not (NO TIENE COBERTURA)
   - Brief justification of the conclusion
   - Reference to applicable coverage guarantees"""
    }
}


def get_template(template_id: str) -> dict:
    """
    Get template definition by ID.
    
    Args:
        template_id: Template identifier
        
    Returns:
        Template dictionary, or default template if not found
    """
    return TEMPLATES.get(template_id, TEMPLATES["completo"])


def get_available_templates() -> dict:
    """
    Get all available templates.
    
    Returns:
        Dictionary of all templates
    """
    return TEMPLATES.copy()


def get_template_list() -> list:
    """
    Get list of template IDs.
    
    Returns:
        List of template IDs
    """
    return list(TEMPLATES.keys())
