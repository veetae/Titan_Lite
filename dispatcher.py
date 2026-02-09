import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

from titan_core.notes.pipeline import process_note, write_csv_outputs
from titan_core.icd import search_icd, get_guideline
from titan_core.labs import process_drop_folder

from agents.soap_validator import validate_soap_payload
from agents.soap_enrich import enrich_soap_note
from agents.lab_summary import fetch_lab_summary
from agents.icd_coder import query_icd_codes  # until this module is refactored too

def auto_route(payload):
    if "subjective" in payload and "chief_complaint" in payload:
        if not validate_soap_payload(payload):
            return {"error": "Invalid SOAP structure"}
        return enrich_soap_note(payload)
    elif "patient_id" in payload and "query" in payload:
        return query_icd_codes({"query": payload["query"]})
    elif "patient_id" in payload and "query" not in payload:
        return fetch_lab_summary({"patient_id": payload["patient_id"]})
    return {"error": "No valid routing logic matched"}
