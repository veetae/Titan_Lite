import os
import datetime
from agents.dispatcher import auto_route
from agents.soap_validator import validate_soap_payload

os.makedirs("output", exist_ok=True)

payload = {
    "patient_id": "12345",
    "subjective": "Patient reports fatigue and dizziness.",
    "chief_complaint": "fatigue",
    "plan": "Order CBC and refer to endocrinology."
}

is_valid = validate_soap_payload(payload)
result = auto_route(payload)

timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
lines = [
    f"Timestamp: {timestamp}",
    f"Validation: {'✅ Valid' if is_valid else '❌ Invalid'}",
    "",
    "=== Enriched SOAP Note ===",
    f"Subjective: {result.get('Subjective', 'N/A')}",
    "Objective:"
]
for lab in result.get("Objective", []):
    lines.append(f"  - {lab}")
lines.append("Assessment:")
for icd in result.get("Assessment", []):
    lines.append(f"  - {icd}")
lines.append(f"Plan: {result.get('Plan', 'N/A')}")
lines.append("Guidelines:")
for guide in result.get("Guidelines", []):
    lines.append(f"  - {guide['title']} ({guide['url']})")

filename = f"output/verified_enrich_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(filename, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"✅ Output saved to: {filename}")
