import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
import jsonschema
import logging

logger = logging.getLogger("SOAPValidator")

SOAP_SCHEMA = {
    "type": "object",
    "properties": {
        "patient_id": {"type": "string"},
        "subjective": {"type": "string"},
        "chief_complaint": {"type": "string"},
        "plan": {"type": "string"}
    },
    "required": ["patient_id", "subjective", "chief_complaint", "plan"]
}

def validate_soap_payload(payload):
    try:
        jsonschema.validate(instance=payload, schema=SOAP_SCHEMA)
        logger.info("âœ… SOAP payload validated")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"âŒ SOAP validation failed: {e.message}")
        return False

