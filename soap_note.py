import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
from agents.lab_summary import fetch_lab_summary
from agents.icd_coder import query_icd_codes
import logging

logger = logging.getLogger("SOAP")

def generate_soap_note(payload):
    patient_id = payload.get("patient_id")
    if not patient_id:
        logger.warning("âš ï¸ Missing patient_id in SOAP payload")
        return None

    labs = fetch_lab_summary({"patient_id": patient_id})
    icds = query_icd_codes({"query": payload.get("chief_complaint", "")})

    note = {
        "Subjective": payload.get("subjective", "N/A"),
        "Objective": labs,
        "Assessment": icds,
        "Plan": payload.get("plan", "Follow-up in 1 week")
    }

    logger.info("ðŸ§¾ SOAP note generated")
    return note

