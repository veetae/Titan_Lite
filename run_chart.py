# C:\titanmind\titan_lite\run_chart.py
import os, sys, re, datetime
import psycopg2
from psycopg2.extras import RealDictCursor

# --- Config ---
DSN = os.environ.get("DATABASE_URL") or (
    "postgresql://neondb_owner:npg_HiR1G5bKxQrN@"
    "ep-small-poetry-afqpq2eb-pooler.c-2.us-west-2.aws.neon.tech/"
    "neondb?sslmode=require&channel_binding=require"
)

SECTION_HINTS = ("subjective","objective","assessment","plan","s:","o:","a:","p:","soap","assessment & plan")

def polish(md: str) -> str:
    """
    Aggressive cleaner:
      - Trim whitespace noise
      - Remove AI/prompt leakage lines
      - Deduplicate consecutive lines and duplicate paragraphs
      - Normalize bullets and mild section headers
      - Keep clinical free text intact
    """
    if not md:
        return md
    s = md.replace("\r\n", "\n")

    # Remove common prompt leakage
    vomit = [
        r"(?i)^as an ai.*$",
        r"(?i)^this (?:is|was) (?:a )?prompt.*$",
        r"(?i)^generate (?:a )?soap note.*$",
        r"(?i)^you asked (?:me )?to.*$",
        r"(?i)^system prompt.*$",
        r"(?i)^assistant(?: message)?:.*$",
        r"(?i)^user(?: message)?:.*$",
        r"(?i)^example(?:s)?:.*$",
        r"(?i)^instruction(?:s)?:.*$",
    ]
    for pat in vomit:
        s = re.sub(pat, "", s, flags=re.M)

    # Remove fenced code blocks / xml-ish wrappers
    s = re.sub(r"(?s)```.*?```", "", s)
    s = re.sub(r"(?s)<(?:system|user|assistant).*?>.*?</(?:system|user|assistant)>", "", s)
    s = re.sub(r"(?i)^\s*#+\s*(prompt|system|assistant|user)\s*$", "", s, flags=re.M)

    # Whitespace normalization
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    s = re.sub(r"[ ]{2,}", " ", s)
    s = s.replace("\t", "  ")
    s = re.sub(r" +([,:;])", r"\1", s)

    # Bullet normalization
    s = re.sub(r"^\s*[-•]\s*", "- ", s, flags=re.M)

    # Deduplicate consecutive identical lines
    lines, prev = [], None
    for line in s.splitlines():
        norm = line.strip()
        if norm and norm == prev:
            continue
        lines.append(line)
        prev = norm
    s = "\n".join(lines)

    # Deduplicate paragraphs (exact-match after whitespace fold)
    seen, out = set(), []
    for para in [p for p in s.split("\n\n") if p.strip()]:
        key = re.sub(r"\s+", " ", para.strip()).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(para)
    s = "\n\n".join(out)

    # Normalize headers lightly
    def _hdr(m):
        t = m.group(0)
        return t[0].upper() + t[1:] if t and t[0].islower() else t
    for h in SECTION_HINTS:
        s = re.sub(rf"(?im)^(#{0,2}\s*){h}\s*[:\-]?\s*$", lambda m: _hdr(m), s)

    return s.strip()
    
SUSPECT_MEDS = {
    # common mis-hears / non-meds to flag
    "naphthalene", "metrolax", "antivenom", "napthalene", "metrolax", "metrolax®"
}

def postprocess_clinical(text: str) -> str:
    """
    - Drop contradictory demographics ("MRN not provided", etc.) if any MRN/age/sex is already present.
    - Flag suspicious meds in [Medication Review] list with [FLAG:?].
    """
    if not text:
        return text

    lines = text.splitlines()
    lower_all = "\n".join(lines).lower()

    # Heuristics: if earlier content contains any credible identifiers, remove "not provided" boilerplate
    has_mrn = "mrn" in lower_all and re.search(r"\bmrn\b\s*[:#]?\s*\w+", lower_all)
    has_age = re.search(r"\b(\d{1,3})\s*y/?o\b|\bage\s*[:]\s*\d{1,3}\b", lower_all)
    has_gender = re.search(r"\b(male|female|man|woman|m|f)\b", lower_all)

    cleaned = []
    for ln in lines:
        ln_l = ln.lower().strip()
        if (has_mrn and "mrn not provided" in ln_l) or \
           (has_age and "age not provided" in ln_l) or \
           (has_gender and "gender not provided" in ln_l):
            continue
        cleaned.append(ln)
    text = "\n".join(cleaned)

    # Flag suspicious meds (only inside Medication Review block if present)
    out, in_meds = [], False
    for ln in text.splitlines():
        ln_stripped = ln.strip()

        # Track entering/leaving meds block
        if re.match(r"^\s*\[?medication review\]?\s*$", ln_stripped, flags=re.I):
            in_meds = True
            out.append(ln)
            continue
        if in_meds and (ln_stripped.startswith("[") and ln_stripped.endswith("]") and
                        not re.match(r"^\s*\[?medication review\]?\s*$", ln_stripped, flags=re.I)):
            # Next bracketed header → meds ended
            in_meds = False

        if in_meds and re.match(r"^\s*[-•]\s*", ln):
            # basic token normalize for matching
            base = re.sub(r"^\s*[-•]\s*", "", ln).strip()
            token = re.split(r"\s|,|\d", base.lower())[0]  # first word before dose
            if token in SUSPECT_MEDS:
                ln = f"{ln}  [FLAG:? verify medication name]"
        out.append(ln)

    return "\n".join(out)
   
 

def fail(msg: str, code: int = 2):
    print(f"ERROR: {msg}")
    sys.exit(code)

def main():
    # Args: --handle <handle>
    if "--handle" in sys.argv:
        i = sys.argv.index("--handle")
        if i + 1 < len(sys.argv):
            handle = sys.argv[i + 1]
        else:
            fail("--handle requires a value", 2)
    else:
        fail("Specify --handle <user_handle> (e.g., demo_builder)", 2)

    out_dir = os.environ.get("MEMORY", os.path.join(os.getcwd(), "Output"))
    os.makedirs(out_dir, exist_ok=True)

    try:
        with psycopg2.connect(DSN) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Health check
                cur.execute(
                    "SELECT to_regclass('titan.users') ok_u, "
                    "       to_regclass('titan.encounters') ok_e, "
                    "       to_regclass('titan.notes') ok_n;"
                )
                r = cur.fetchone()
                if not all([r["ok_u"], r["ok_e"], r["ok_n"]]):
                    fail("titan schema missing; run init/reset.", 3)

                # Pull latest note for handle
                cur.execute("""
                    SELECT n.note_id, n.note_type, n.content_md, n.status, n.validator,
                           e.dos, u.handle
                    FROM titan.notes n
                    JOIN titan.encounters e ON e.enc_id = n.enc_id
                    JOIN titan.users u ON u.user_id = e.user_id
                    WHERE u.handle = %s
                    ORDER BY n.created_at DESC
                    LIMIT 1
                """, (handle,))
                row = cur.fetchone()
                if not row:
                    fail(f"No notes found for handle={handle}", 4)

                content = row["content_md"] or ""
                polished = postprocess_clinical(polish(content))

                # Non-destructive in-DB update if content changed
                if polished != content:
                    cur.execute("""
                        UPDATE titan.notes
                           SET content_md = %s,
                               validator  = COALESCE(NULLIF(validator,''),'TitanPolish v2') ||
                                            CASE
                                              WHEN validator IS NULL OR validator='' THEN ''
                                              ELSE ';TitanPolish v2'
                                            END
                         WHERE note_id = %s
                    """, (polished, row["note_id"]))
                    conn.commit()

                # Emit chart-ready text file
                dos = row["dos"] or datetime.date.today()
                fname = f"chart_{handle}_{dos.isoformat()}.txt"
                fpath = os.path.join(out_dir, fname)

                header = [
                    f"Handle: {row['handle']}",
                    f"DOS: {dos.isoformat()}",
                    f"Type: {row['note_type']}",
                    f"Status: {row['status']}",
                    f"Validator: {row['validator'] or '—'}",
                    "-" * 64
                ]
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write("\n".join(header) + "\n" + polished + "\n")

                print(f"OK: wrote {fpath}")

    except psycopg2.Error as e:
        fail(f"Database error: {e.pgerror or e}", 4)
    except Exception as e:
        fail(f"Runtime error: {e}", 5)

if __name__ == "__main__":
    main()
