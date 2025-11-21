import sys
from agents.icd_coder import query_icd_codes
from agents.lab_summary import fetch_lab_summary
from agents.soap_enrich import enrich_soap_note
from agents.mcp_bridge import orchestrate_agent
from agents.dispatcher import auto_route
content = row["content_md"] or ""
polished = polish(content)


payload = {
    "patient_id": "12345",
    "subjective": "Patient reports fatigue and dizziness.",
    "chief_complaint": "fatigue",
    "plan": "Order CBC and refer to endocrinology."
}

result = auto_route(payload)
print("🧠 Routed Result:", result)


# CLI task
task = sys.argv[1] if len(sys.argv) > 1 else "default"

# Shared payload
payload = {
    "patient_id": "12345",
    "query": "diabetes",
    "subjective": "Patient reports fatigue.",
    "chief_complaint": "fatigue",
    "plan": "Order CBC and refer to endocrinology."
}

# Direct agent calls
if task == "icd_lookup":
    print("🔍 ICD Lookup Result:")
    print(query_icd_codes({"query": payload["query"]}))

elif task == "lab_summary":
    print("🧪 Lab Summary Result:")
    print(fetch_lab_summary({"patient_id": payload["patient_id"]}))

elif task == "soap_enrich":
    print("🧾 Enriched SOAP Note:")
    print(enrich_soap_note(payload))

elif task == "mcp_icd":
    print("🧠 MCP Orchestrated ICD Lookup:")
    result = orchestrate_agent("icd_lookup", {"patient_id": payload["patient_id"], "query": payload["query"]})
    print(result)

else:
    print("⚠️ Unknown task. Use one of: icd_lookup, lab_summary, soap_enrich, mcp_icd")
