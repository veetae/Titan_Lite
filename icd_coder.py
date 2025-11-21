import os, sys
_root = os.path.dirname(os.path.dirname(__file__))
if _root not in sys.path:
    sys.path.insert(0, _root)

import logging
from utils.validator import validate_payload
from utils.retry import retry_with_backoff
from titan_core.icd import search_icd

logger = logging.getLogger("ICD")

def query_icd_codes(payload):
    if not validate_payload(payload, "icd_lookup"):
        logger.warning("⚠️ Invalid ICD payload")
        return None
    query = payload.get("query", "")
    if not query:
        return []
    return retry_with_backoff(lambda: search_icd(query))
