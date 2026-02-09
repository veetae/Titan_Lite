import re

def polish_note(md: str) -> str:
    """
    Aggressive cleaner:
      - Trim whitespace noise
      - Remove AI/prompt leakage lines (e.g., 'As an AI...', 'Generate SOAP note...')
      - Deduplicate consecutive lines and duplicate paragraphs
      - Normalize bullets and mild section headers
      - Keep free-text clinical content intact
    """
    if not md:
        return md

    s = md.replace("\r\n", "\n")

    # --- strip obvious prompt leakage / vomit (line-based) ---
    # add more patterns as needed; kept conservative for safety
    VOMIT_PATTERNS = [
        r"(?i)^as an ai.*$",
        r"(?i)^this (?:is|was) (?:a )?prompt.*$",
        r"(?i)^generate (?:a )?soap note.*$",
        r"(?i)^you asked (?:me )?to.*$",
        r"(?i)^system prompt.*$",
        r"(?i)^assistant(?: message)?:.*$",
        r"(?i)^user(?: message)?:.*$",
        r"(?i)^example(?:s)?:.*$",
        r"(?i)^instruction(?:s)?:.*$",
        r"(?i)^do not (?:include|remove).*$",
    ]
    for pat in VOMIT_PATTERNS:
        s = re.sub(pat, "", s, flags=re.M)

    # remove fenced code blocks and HTML-like prompt scaffolds
    s = re.sub(r"(?s)```.*?```", "", s)            # fenced code
    s = re.sub(r"(?s)<(?:system|user|assistant).*?>.*?</(?:system|user|assistant)>", "", s)
    s = re.sub(r"(?i)^\s*#+\s*(prompt|system|assistant|user)\s*$", "", s, flags=re.M)

    # --- whitespace normalization ---
    s = re.sub(r"[ \t]+\n", "\n", s)               # trailing spaces
    s = re.sub(r"\n{3,}", "\n\n", s)               # >2 blank lines → 1
    s = re.sub(r"[ ]{2,}", " ", s)                 # multi-spaces
    s = s.replace("\t", "  ")
    s = re.sub(r" +([,:;])", r"\1", s)             # trim space before punctuation

    # --- bullet normalization ---
    s = re.sub(r"^\s*[-•]\s*", "- ", s, flags=re.M)

    # --- deduplicate consecutive identical lines ---
    lines, prev = [], None
    for line in s.splitlines():
        norm = line.strip()
        if norm and norm == prev:
            continue
        lines.append(line)
        prev = norm
    s = "\n".join(lines)

    # --- deduplicate paragraphs (exact-match) ---
    seen, out = set(), []
    for para in [p for p in s.split("\n\n") if p.strip()]:
        key = re.sub(r"\s+", " ", para.strip()).lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(para)
    s = "\n\n".join(out)

    # --- normalize common headers lightly (keep content) ---
    SECTION_HINTS = ("subjective","objective","assessment","plan","s:","o:","a:","p:","soap","assessment & plan")
    def _hdr(text: str) -> str:
        return text[0].upper() + text[1:] if text and text[0].islower() else text
    for h in SECTION_HINTS:
        pat = re.compile(fr"(?im)^(?:#{{0,2}}\s*){re.escape(h)}\s*[:\-]?\s*$")
        s = pat.sub(lambda m: _hdr(m.group(0)), s)

    return s.strip()
