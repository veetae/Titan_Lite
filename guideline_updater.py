# guideline_updater.py
import json

def add_guideline(icd, source, recommendations, path="guideline_map.json"):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    data[icd] = {"source": source, "recommendations": recommendations}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)