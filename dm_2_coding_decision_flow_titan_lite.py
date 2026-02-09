"""
DM2_Coding_Decision_Flow (Titan_Lite)
One-file decision engine that converts structured flags → ICD-10 codes (+ rationale).
Drop this in: C:\titanmind\titan_lite\Agent\dm2_coding_flow.py

USAGE (PowerShell):
  cd C:\titanmind\titan_lite
  .\.venv\Scripts\Activate.ps1
  python .\Agent\dm2_coding_flow.py --demo

PROGRAMMATIC (inside your agents):
  from Agent.dm2_coding_flow import decide_dm2_codes, DM2Input
  result = decide_dm2_codes(DM2Input(...))
  print(result.icd_codes, result.rationales)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple
import argparse

# ----------------------------
# Inputs (extend as needed)
# ----------------------------
@dataclass
class DM2Input:
    # Step 1: Base
    on_insulin: bool  # True if currently on insulin
    # Step 2: Glycemic control
    a1c_percent: Optional[float] = None  # latest HbA1c
    # Renal
    uacr_mg_per_g: Optional[float] = None  # urine albumin/creatinine ratio
    egfr: Optional[float] = None
    # Eye
    diabetic_retinopathy: Optional[bool] = None
    macular_edema: Optional[bool] = None
    # Neuro
    neuropathy_unspecified: Optional[bool] = None
    neuropathy_poly: Optional[bool] = None
    # Circulatory
    pvd: Optional[bool] = None
    gangrene: Optional[bool] = None
    # Skin/MSK
    foot_ulcer: Optional[bool] = None
    arthropathy: Optional[bool] = None
    other_skin_comp: Optional[bool] = None
    # Risk modules
    cv_status: Optional[str] = None  # 'Very High', 'High', 'CAD', 'PriorEvent'
    # Lipids
    ldl_mg_dl: Optional[float] = None
    statin_intolerant: Optional[bool] = None
    # BP / HTN
    sbp: Optional[int] = None
    dbp: Optional[int] = None
    # Obesity
    bmi: Optional[float] = None
    # Mental health
    depression: Optional[bool] = None
    anxiety: Optional[bool] = None

@dataclass
class Decision:
    icd_codes: List[str]
    rationales: List[str]
    advisories: List[str]

# ----------------------------
# Core logic
# ----------------------------

def decide_dm2_codes(x: DM2Input) -> Decision:
    codes: List[str] = []
    why: List[str] = []
    adv: List[str] = []

    # Step 1 + 2: Base DM2
    base = None
    if x.on_insulin:
        base = "E11.65"  # DM2 with hyperglycemia (maps to insulin use OR uncontrolled)
        why.append("On insulin → treat as hyperglycemia phenotype (E11.65)")
    else:
        # Use A1c to decide E11.65 vs E11.9
        if x.a1c_percent is not None and x.a1c_percent >= 7.0:
            base = "E11.65"
            why.append(f"A1c {x.a1c_percent:.1f}% ≥7.0 → E11.65")
        else:
            base = "E11.9"
            why.append("A1c <7% and not on insulin → E11.9")
    codes.append(base)

    # Complications by system
    # Renal
    if x.uacr_mg_per_g is not None:
        if 30 <= x.uacr_mg_per_g < 300:
            codes.append("E11.29"); why.append(f"UACR {x.uacr_mg_per_g} mg/g → renal complication (E11.29)")
        elif x.uacr_mg_per_g >= 300:
            codes.append("E11.21"); why.append(f"UACR {x.uacr_mg_per_g} mg/g (≥300) → diabetic nephropathy (E11.21)")
    if x.egfr is not None and x.egfr < 60:
        if "E11.22" not in codes:
            codes.append("E11.22"); why.append(f"eGFR {x.egfr} <60 → diabetic CKD (E11.22)")

    # Eye
    if x.diabetic_retinopathy:
        if x.macular_edema:
            codes.append("E11.311"); why.append("Retinopathy with macular edema → E11.311")
        else:
            codes.append("E11.319"); why.append("Retinopathy (unspecified) → E11.319")

    # Neuro
    if x.neuropathy_poly:
        codes.append("E11.42"); why.append("Diabetic polyneuropathy → E11.42")
    elif x.neuropathy_unspecified:
        codes.append("E11.40"); why.append("Diabetic neuropathy, unspecified → E11.40")

    # Circulatory
    if x.pvd:
        if x.gangrene:
            codes.append("E11.52"); why.append("PVD with gangrene → E11.52")
        else:
            codes.append("E11.51"); why.append("PVD without gangrene → E11.51")

    # Skin/MSK
    if x.foot_ulcer:
        codes.append("E11.621"); why.append("Diabetic foot ulcer → E11.621")
    if x.arthropathy:
        codes.append("E11.610"); why.append("Diabetic arthropathy → E11.610")
    if x.other_skin_comp:
        codes.append("E11.628"); why.append("Other skin complications → E11.628")

    # Cardiovascular risk adjunct coding (non-exhaustive; adjust per clinic policy)
    if x.cv_status:
        cv = x.cv_status.lower()
        if cv in ("very high", "high"):
            codes.append("E11.59")  # DM with circulatory complications (umbrella)
            why.append("CV risk high → capture circulatory complications umbrella (E11.59)")
        if cv == "cad":
            codes.append("I25.10"); why.append("Established CAD without angina → I25.10")
        if cv == "priorevent":
            codes.append("Z87.891"); why.append("History of CVD/risk → Z87.891 (per clinic tag)")

    # Lipids targets advisories (not codes by themselves)
    if x.ldl_mg_dl is not None:
        ldl_goal = 55 if (x.cv_status and x.cv_status.lower() in ("cad","priorevent")) else 70
        if x.ldl_mg_dl > ldl_goal:
            adv.append(f"LDL {x.ldl_mg_dl} mg/dL > goal ({ldl_goal}) — intensify statin/ezetimibe/PCSK9 per guidelines")
    if x.statin_intolerant:
        codes.append("Z88.1"); why.append("Statin intolerance/allergy → Z88.1")

    # Hypertension
    if x.sbp is not None and x.dbp is not None:
        htn_uncontrolled = (x.sbp >= 130 or x.dbp >= 80)
        codes.append("I10"); why.append("Essential hypertension (I10)")
        if htn_uncontrolled:
            codes.append("Z79.899"); why.append("On long-term meds; uncontrolled BP context → Z79.899")

    # BMI / Obesity
    if x.bmi is not None:
        if x.bmi >= 40:
            codes.append("E66.01"); why.append("BMI ≥40 → Morbid obesity due to excess calories (E66.01)")
        elif x.bmi >= 35:
            codes.append("E66.01"); why.append("BMI 35–39.9 → Treat as Class II/III per clinic policy (E66.01)")
        elif x.bmi >= 30:
            codes.append("E66.9"); why.append("BMI 30–34.9 → Obesity (E66.9)")
        elif x.bmi >= 25:
            codes.append("Z68.25"); why.append("BMI 25–29.9 → Overweight code series (use exact Z68.2x if available)")

    # Mental health
    if x.depression and x.anxiety:
        codes.append("F41.8"); why.append("Mixed anxiety/depressive features → F41.8")
    else:
        if x.depression:
            codes.append("F32.9"); why.append("Depression, unspecified → F32.9")
        if x.anxiety:
            codes.append("F41.9"); why.append("Anxiety, unspecified → F41.9")

    # Deduplicate preserving order
    seen = set(); dedup_codes = []
    for c in codes:
        if c not in seen:
            seen.add(c); dedup_codes.append(c)

    return Decision(icd_codes=dedup_codes, rationales=why, advisories=adv)

# ----------------------------
# CLI demo
# ----------------------------

def _demo():
    sample = DM2Input(
        on_insulin=False,
        a1c_percent=8.1,
        uacr_mg_per_g=220,
        egfr=58,
        diabetic_retinopathy=True,
        macular_edema=False,
        neuropathy_poly=True,
        pvd=True,
        gangrene=False,
        cv_status="High",
        ldl_mg_dl=92,
        statin_intolerant=False,
        sbp=142, dbp=82,
        bmi=33.5,
        depression=False,
        anxiety=True,
    )
    d = decide_dm2_codes(sample)
    print("ICD:", ", ".join(d.icd_codes))
    print("-"*64)
    print("Rationales:")
    for r in d.rationales:
        print(" •", r)
    if d.advisories:
        print("Advisories:")
        for a in d.advisories:
            print(" •", a)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    if args.demo:
        _demo()
