"""Claim data parser to extract structured information from pasted text."""

import re
from typing import Dict, Optional, Any


class ClaimDataParser:
    """Parses unstructured claim data into structured format."""

    def parse_claim_data(self, raw_text: str) -> Dict[str, Any]:
        """
        Parse raw claim data text into structured dictionary.

        Args:
            raw_text: Raw text containing claim information

        Returns:
            Dictionary with parsed claim data
        """
        parsed = {
            "policy_number": None,
            "dni": None,
            "insured_name": None,
            "address": None,
            "catastral_reference": None,
            "claim_description": None,
            "service_reason": None,
            "cause": None,
            "raw_text": raw_text,
        }

        # Normalize text
        text = raw_text.strip()

        # Extract Policy Number
        policy_match = re.search(r'(?i)(?:póliza|poliza|policy)[\s:]*(\d+)', text)
        if policy_match:
            parsed["policy_number"] = policy_match.group(1).strip()

        # Extract DNI
        dni_match = re.search(r'(?i)(?:dni|nif)[\s:]*([A-Z0-9]{8,9})', text)
        if dni_match:
            parsed["dni"] = dni_match.group(1).strip().upper()

        # Extract Asegurado (Insured Name)
        insured_match = re.search(r'(?i)(?:asegurado|insured)[\s:]*([A-ZÁÉÍÓÚÑ\s]+(?:\s[A-ZÁÉÍÓÚÑ\s]+)*)', text)
        if insured_match:
            parsed["insured_name"] = insured_match.group(1).strip()

        # Extract Domicilio (Address)
        address_match = re.search(r'(?i)(?:domicilio|address|dirección)[\s:]*([^\n]+)', text)
        if address_match:
            parsed["address"] = address_match.group(1).strip()

        # Extract Referencia Catastral
        catastral_match = re.search(r'(?i)(?:referencia\s+catastral|catastral)[\s:]*([A-Z0-9\s]+)', text)
        if catastral_match:
            parsed["catastral_reference"] = catastral_match.group(1).strip()

        # Extract Descripción del Siniestro (Claim Description)
        desc_match = re.search(r'(?i)(?:descripción\s+del\s+siniestro|description)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Motivo|Causa|$))', text, re.MULTILINE | re.DOTALL)
        if desc_match:
            parsed["claim_description"] = desc_match.group(1).strip()

        # Extract Motivo de Alta (Service Reason)
        motivo_match = re.search(r'(?i)(?:motivo\s+de\s+alta|service\s+reason)[\s:]*([^\n]+(?:\n[^\n]+)*?)(?=\n(?:Causa|$))', text, re.MULTILINE | re.DOTALL)
        if motivo_match:
            parsed["service_reason"] = motivo_match.group(1).strip()

        # Extract Causa (Cause)
        causa_match = re.search(r'(?i)(?:causa|cause)[\s:]*([^\n]+)', text)
        if causa_match:
            parsed["cause"] = causa_match.group(1).strip()

        # Build search query from available data
        search_terms = []
        if parsed["cause"]:
            search_terms.append(parsed["cause"])
        if parsed["claim_description"]:
            # Extract key phrases from description (first 200 chars)
            desc_short = parsed["claim_description"][:200]
            search_terms.append(desc_short)
        if parsed["service_reason"]:
            # Extract key phrases from service reason
            search_terms.append(parsed["service_reason"][:200])

        parsed["search_query"] = " ".join(search_terms) if search_terms else parsed["claim_description"] or parsed["raw_text"][:500]

        return parsed

    def extract_keywords(self, text: str) -> list:
        """
        Extract keywords from text for search.

        Args:
            text: Text to extract keywords from

        Returns:
            List of keywords
        """
        if not text:
            return []

        # Remove common words and extract meaningful terms
        # Simple approach: extract words that are likely to be relevant
        words = re.findall(r'\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\b|\b[a-záéíóúñ]{4,}\b', text.lower())
        
        # Filter out very common words
        stop_words = {'que', 'del', 'las', 'los', 'una', 'por', 'con', 'para', 'esta', 'este', 'está', 'están'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Return unique keywords, limit to top 10
        return list(set(keywords))[:10]
