from __future__ import annotations
from pathlib import Path
from typing import Dict, Any, List, Optional
import json
import re

from polish_notes import polish_note


def clean(md: str) -> str:
    # basic whitespace cleanup before polish
    if not md:
        return md
    s = md.replace('\r\n', '\n')
    s = re.sub(r'\u200b|\uFEFF', '', s)  # zero-width chars
    return s.strip()


def minimal_language_polish(md: str) -> str:
    """Very conservative grammar/spelling touch-ups without changing meaning."""
    if not md:
        return md
    s = md
    # common typos (add more over time)
    fixes = {
        ' teh ': ' the ',
        ' patiet ': ' patient ',
        ' paitent ': ' patient ',
        ' diabetse': ' diabetes',
        ' diabtes': ' diabetes',
        ' hypertesion': ' hypertension',
        ' bp ': ' BP ',
    }
    for k, v in fixes.items():
        s = s.replace(k, v)
    # punctuation spacing
    s = re.sub(r"\s+([,.;:!?])", r"\1", s)
    s = re.sub(r"([,.;:!?])(\S)", r"\1 \2", s)
    return s


def arrange_flow_sections(md: str) -> str:
    """Reorder to Subjective, Objective, Assessment, Plan, Follow-up if present.
    Keep other content at the end. If Plan missing/too short, add a placeholder and TODO.
    """
    if not md:
        return md
    text = md
    # Split by headings
    pattern = re.compile(r"(?im)^(#{0,2}\s*(subjective|objective|assessment|plan|follow-?up))\s*[:\-]?\s*$")
    parts: List[Dict[str, Any]] = []
    last = 0
    current = None
    for m in pattern.finditer(text):
        if current is not None:
            current['content'] = text[last:m.start()].strip('\n')
            parts.append(current)
        current = {'header': m.group(1), 'key': m.group(2).lower()}
        last = m.end()
    if current is not None:
        current['content'] = text[last:].strip('\n')
        parts.append(current)
    if not parts:
        # no recognizable headers; just return as-is
        return text
    by_key: Dict[str, str] = {}
    for p in parts:
        by_key[p['key'].replace('followup', 'follow-up')] = p.get('content', '')
    order = ['subjective', 'objective', 'assessment', 'plan', 'follow-up']
    out_sections: List[str] = []
    for key in order:
        content = by_key.get(key) or ''
        if content:
            title = key.title().replace('Follow-Up', 'Follow-up')
            out_sections.append(f"{title}\n\n{content.strip()}\n")
    # Plan placeholder if missing/too short
    plan_text = by_key.get('plan', '').strip() if by_key.get('plan') is not None else ''
    if not plan_text or len(plan_text) < 20:
        placeholder = "Plan\n\nTo be addressed in next visit:\n- Pending review/updates.\n"
        # Insert after Assessment or at end
        inserted = False
        rebuilt: List[str] = []
        for sec in out_sections:
            rebuilt.append(sec)
            if sec.lower().startswith('assessment') and not inserted:
                rebuilt.append(placeholder)
                inserted = True
        if not inserted:
            rebuilt.append(placeholder)
        out_sections = rebuilt
    # Ensure Follow-up exists
    if 'follow-up' not in by_key:
        out_sections.append("Follow-up\n\nAs scheduled.\n")
    # Append TODO list after Follow-up
    out_sections.append("TODO\n\n- Review plan items next visit.\n")
    return "\n\n".join(s.strip() for s in out_sections if s.strip())


def validate_minimal(md: str) -> Dict[str, Any]:
    # lightweight validation: presence of content and size sanity
    issues: List[str] = []
    if not md or not md.strip():
        issues.append('empty_note')
    if len(md) < 20:
        issues.append('too_short')
    if len(md) > 200000:
        issues.append('too_long')
    return {'valid': len(issues) == 0, 'issues': issues}


def enrich(md: str) -> Dict[str, Any]:
    # derive simple metadata and section hints
    text = md or ''
    words = re.findall(r"\b\w+\b", text)
    lines = [l for l in text.splitlines() if l.strip()]
    sections = []
    for h in ('subjective', 'objective', 'assessment', 'plan', 'soap'):
        if re.search(fr"(?im)^\s*{re.escape(h)}\s*[:\-]?\s*$", text):
            sections.append(h)
    return {
        'chars': len(text),
        'words': len(words),
        'lines': len(lines),
        'sections_detected': sections,
    }


def assign_codes(md: str, icd_csv: Optional[Path] = None, top_n: int = 5) -> List[Dict[str, Any]]:
    # naive ICD matcher: match frequent tokens (>=5 chars) in description
    if not icd_csv:
        icd_csv = Path(__file__).parent / 'icd' / 'icd10_full.csv'
    text = (md or '').lower()
    # pick candidate tokens
    tokens = [t.lower() for t in re.findall(r"[A-Za-z][A-Za-z\-]{4,}", text)]
    uniq = sorted(set(tokens), key=lambda t: (-tokens.count(t), t))[:20]
    matches: List[Dict[str, Any]] = []
    if not icd_csv.exists():
        return matches
    try:
        import csv
        with icd_csv.open('r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            # assume columns: code, description (best-effort)
            for row in reader:
                if not row:
                    continue
                code = row[0].strip() if len(row) > 0 else ''
                desc = row[1].strip().lower() if len(row) > 1 else ''
                if not code or not desc:
                    continue
                score = sum(1 for t in uniq if t in desc)
                if score > 0:
                    matches.append({'code': code, 'description': desc, 'score': score})
        matches.sort(key=lambda x: (-x['score'], x['code']))
        return matches[:top_n]
    except Exception:
        return []


def process_note(md: str) -> Dict[str, Any]:
    cleaned = clean(md)
    polished = polish_note(cleaned)
    polished = minimal_language_polish(polished)
    final_note = arrange_flow_sections(polished)
    v = validate_minimal(polished)
    meta = enrich(polished)
    codes = assign_codes(polished)
    return {
        'cleaned': cleaned,
        'polished': polished,
        'final': final_note,
        'validation': v,
        'enrichment': meta,
        'codes': codes,
    }


def _append_csv(path: Path, header: List[str], rows: List[List[Any]]):
    import csv
    path.parent.mkdir(parents=True, exist_ok=True)
    exists = path.exists()
    with path.open('a', encoding='utf-8', newline='') as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(header)
        for r in rows:
            w.writerow(r)


def write_csv_outputs(result: Dict[str, Any], visit_id: str, output_dir: Optional[Path] = None) -> Dict[str, str]:
    """Append structured rows into Output/master_visit_structured.csv and
    Output/master_visit_structured_ICD_block.csv

    Returns dict of file paths written.
    """
    if output_dir is None:
        output_dir = Path(__file__).parent / 'Output'

    meta = result.get('enrichment', {}) or {}
    valid = bool(result.get('validation', {}).get('valid', False))
    issues = result.get('validation', {}).get('issues', []) or []
    sections = meta.get('sections_detected', []) or []

    # master_visit_structured
    mvs_path = output_dir / 'master_visit_structured.csv'
    mvs_header = ['visit_id', 'chars', 'words', 'lines', 'sections_detected', 'valid', 'issues']
    mvs_row = [
        visit_id,
        meta.get('chars', 0),
        meta.get('words', 0),
        meta.get('lines', 0),
        ';'.join(sections),
        'TRUE' if valid else 'FALSE',
        ';'.join(issues),
    ]
    _append_csv(mvs_path, mvs_header, [mvs_row])

    # master_visit_structured_ICD_block
    icd_path = output_dir / 'master_visit_structured_ICD_block.csv'
    icd_header = ['visit_id', 'code', 'description', 'score']
    icd_rows: List[List[Any]] = []
    for item in result.get('codes', []) or []:
        icd_rows.append([
            visit_id,
            item.get('code', ''),
            item.get('description', ''),
            item.get('score', 0),
        ])
    if icd_rows:
        _append_csv(icd_path, icd_header, icd_rows)

    return {'structured': str(mvs_path), 'icd_block': str(icd_path)}
