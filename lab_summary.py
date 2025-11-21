import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)
from db.neon_wrapper import run_query
from utils.validator import validate_payload
from utils.retry import retry_with_backoff
import logging

logger = logging.getLogger("LabSummary")

def fetch_lab_summary(payload):
    if not validate_payload(payload, "lab_summary"):
        logger.warning("âš ï¸ Invalid lab summary payload")
        return None

    query = f"""
        SELECT test_name, result, units, timestamp
        FROM labs
        WHERE patient_id = '{payload['patient_id']}'
        ORDER BY timestamp DESC
        LIMIT 20
    """

    return retry_with_backoff(lambda: run_query(query))

