import json

def crosscheck_guidelines(note: str, icd_tags: list) -> list:
    enrichments = []
    try:
        with open("C:\\TitanHQ\\Clinical_Processor\\guideline_map.json", "r") as f:
            guideline_map = json.load(f)
    except Exception as e:
        return [f"Guideline map load error: {str(e)}"]

    for icd in icd_tags:
        if icd in guideline_map:
            for rec in guideline_map[icd]["recommendations"]:
                if rec.lower().split()[0] not in note.lower():
                    enrichments.append(f"{guideline_map[icd]['source']}: {rec}")

    return enrichments