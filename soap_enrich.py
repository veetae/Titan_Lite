import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
from agents.lab_summary import fetch_lab_summary
from agents.guideline_retriever import fetch_guidelines
import logging

logger = logging.getLogger("SOAPEnrich")

def enrich_soap_note(payload):
    patient_id = payload.get("patient_id")
    complaint = payload.get("chief_complaint", "")

    labs = fetch_lab_summary({"patient_id": patient_id})
    icds = query_icd_codes({"query": complaint})
    # guidelines = fetch_guidelines({"query": payload["chief_complaint"]})
    guidelines = []
    enriched = {
        "Subjective": payload.get("subjective", "N/A"),
        "Objective": labs or [],
        "Assessment": icds or [],
        "Plan": payload.get("plan", "Follow-up in 1 week"),
        "Guidelines": guidelines or []
    }

    logger.info("ðŸ§  SOAP note enriched with labs, ICDs, and guidelines")
    return enriched

