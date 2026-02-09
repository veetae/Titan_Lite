import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
from agents.icd_coder import query_icd_codes
from agents.lab_summary import fetch_lab_summary
from agents.soap_enrich import enrich_soap_note
from agents.soap_validator import validate_soap_payload
import datetime, os

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
log_path = f"output/agent_health_{timestamp}.txt"

def log(msg):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

try:
    log("âœ… ICD Lookup: " + str(query_icd_codes({"query": "diabetes"})))
    log("âœ… Lab Summary: " + str(fetch_lab_summary({"patient_id": "12345"})))
    log("âœ… SOAP Enrich: " + str(enrich_soap_note({
        "patient_id": "12345",
        "subjective": "Fatigue",
        "chief_complaint": "Fatigue",
        "plan": "Order CBC"
    })))
    log("âœ… SOAP Validation: " + str(validate_soap_payload({
        "subjective": "Fatigue",
        "chief_complaint": "Fatigue"
    })))
except Exception as e:
    log("âŒ Error: " + str(e))

print(f"ðŸ“„ Health check log saved to: {log_path}")
