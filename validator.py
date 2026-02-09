import jsonschema
import logging

SCHEMAS = {
    "lab_summary": {
        "type": "object",
        "properties": {
            "patient_id": {"type": "string"}
        },
        "required": ["patient_id"]
    },
    "icd_lookup": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}

def validate_payload(payload, schema_name):
    schema = SCHEMAS.get(schema_name)
    if not schema:
        logging.warning(f"⚠️ No schema found for: {schema_name}")
        return False
    try:
        jsonschema.validate(instance=payload, schema=schema)
        logging.info("✅ Payload validated")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"❌ Validation failed: {e.message}")
        return False
        
