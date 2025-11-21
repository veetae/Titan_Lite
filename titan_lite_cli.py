#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

from lite_pipeline import process_note, write_csv_outputs


def main():
    ap = argparse.ArgumentParser(description='Titan Lite note processor (clean, validate, polish, enrich, assign codes)')
    ap.add_argument('--in', dest='in_path', help='Input file (Markdown/TXT). If omitted, read stdin')
    ap.add_argument('--out', dest='out_path', help='Output JSON path (default: print to stdout)')
    ap.add_argument('--id', dest='visit_id', help='Visit/Note identifier (default: input filename stem or "stdin")')
    ap.add_argument('--no-json', action='store_true', help='Do not emit JSON (still writes CSV sheets)')
    ns = ap.parse_args()

    if ns.in_path:
        text = Path(ns.in_path).read_text(encoding='utf-8', errors='replace')
    else:
        text = sys.stdin.read()

    result = process_note(text)

    # Determine visit_id
    if ns.visit_id:
        visit_id = ns.visit_id
    elif ns.in_path:
        visit_id = Path(ns.in_path).stem
    else:
        visit_id = 'stdin'

    # Always write structured CSV sheets in Output/
    write_csv_outputs(result, visit_id)

    # JSON output (optional)
    if not ns.no-json:
        if ns.out_path:
            Path(ns.out_path).parent.mkdir(parents=True, exist_ok=True)
            Path(ns.out_path).write_text(json.dumps(result, indent=2), encoding='utf-8')
        else:
            print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
