import os
import re
import time
from datetime import datetime, timedelta
import pyperclip
import sys, subprocess  # add

HANDLE_INSERT = "demo_builder"                # Titan_Lite handle
TITAN_ROOT    = r"C:\titanHQ\titan_lite"    # Titan_Lite root (ensure path exists)
CHECK_INTERVAL = 1

# ---------- Folder selection ----------
def choose_save_folder():
    print("\nSelect drop folder for saved notes.")
    print(" - Press Enter to use a detected default (if shown).")
    print(" - Or paste/type a full path to a folder.")

    candidates = [
        r"C:\titanHQ\titan_lite\Drop",                           # <- standardize here
        r"C:\Users\veeta\OneDrive\titanHQ_core_one\drop",
        r"C:\Users\KMSM\Onedrive\titanHQ_core_one\drop",
        os.path.join(os.getcwd(), "drop"),
    ]
    default = next((p for p in candidates if os.path.exists(p)), None)
    if default:
        print(f"Detected default: {default}")

    while True:
        raw = input("Folder path (Enter to accept default): ").strip('" ').strip()
        path = raw or default
        if not path:
            print("No default found. Please provide a valid folder path.")
            continue
        try:
            os.makedirs(path, exist_ok=True)
            return os.path.abspath(path)
        except Exception as e:
            print(f"Invalid path or cannot create folder: {e}. Try again.")

# ---------- Name parsing ----------
NAME_PATTERNS = [
    r"Patient\s+([A-Z][a-zA-Z'`-]+(?:\s+[A-Z][a-zA-Z'`-]+)+)\s*,\s*MRN\b",
    r"Patient\s*:\s*([A-Z][a-zA-Z'`-]+(?:\s+[A-Z][a-zA-Z'`-]+)+)\b",
    r"Patient\s+([A-Z][a-zA-Z'`-]+(?:\s+[A-Z][a-zA-Z'`-]+)+)\b",
    r"\bName\s*:\s*([A-Z][a-zA-Z'`-]+(?:\s+[A-Z][a-zA-Z'`-]+)+)\b",
]
INVALID_FS_CHARS = r'<>:"/\|?*'

def sanitize_filename_component(s: str) -> str:
    table = str.maketrans({c: "_" for c in INVALID_FS_CHARS})
    s = s.translate(table).strip()
    s = re.sub(r"\s+", " ", s)
    s = s.replace(" ", "_")
    return s or "UNKNOWN"

def try_extract_patient_name(text: str) -> str:
    for pat in NAME_PATTERNS:
        m = re.search(pat, text)
        if m:
            return sanitize_filename_component(m.group(1))
    return "UNKNOWN"

def prompt_patient_name_if_unknown(current: str) -> str:
    if current != "UNKNOWN":
        return current
    print("\nCould not parse patient name from note.")
    manual = input("Enter patient name (e.g., John Doe), or press Enter to keep UNKNOWN: ").strip()
    if manual:
        if re.match(r"^[A-Za-z][A-Za-z'`-]+(\s+[A-Za-z][A-Za-z'`-]+)+$", manual):
            return sanitize_filename_component(manual)
        else:
            print("Invalid format. Keeping as UNKNOWN.")
    return "UNKNOWN"

# ---------- Date handling ----------
def get_note_date() -> str | None:
    while True:
        try:
            print("\nEnter encounter date:")
            print("  - Enter/t : today (year forced to 2025)")
            print("  - y       : yesterday (year forced to 2025)")
            print("  - MM-DD   : month-day with year forced to 2025")
            print("  - YYYY-MM-DD")
            date_input = input("Date: ").strip().lower()

            if not date_input or date_input == 't':
                today = datetime.now()
                note_date = f"2025-{today.strftime('%m-%d')}"
            elif date_input == 'y':
                yest = datetime.now() - timedelta(days=1)
                note_date = f"2025-{yest.strftime('%m-%d')}"
            elif '-' in date_input and len(date_input) == 5:
                note_date = f"2025-{date_input}"
            else:
                datetime.strptime(date_input, '%Y-%m-%d')
                note_date = date_input

            datetime.strptime(note_date, '%Y-%m-%d')
            return note_date

        except ValueError:
            print("Invalid format. Use YYYY-MM-DD or MM-DD.")
        except KeyboardInterrupt:
            print("\nCancelled.")
            return None

# ---------- Core processing ----------
def process_soap_note(clipboard_text: str, save_folder: str) -> bool:
    if len(clipboard_text or "") < 200:
        return False
    if 'Patient' not in clipboard_text:
        return False

    patient_name = try_extract_patient_name(clipboard_text)
    print(f"\nDetected patient: {patient_name.replace('_', ' ')}" if patient_name != "UNKNOWN" else "\nDetected patient: UNKNOWN")
    patient_name = prompt_patient_name_if_unknown(patient_name)

    note_date = get_note_date()
    if not note_date:
        return False

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    filename  = f"{patient_name}_SOAP_{note_date}.txt"
    filepath  = os.path.join(save_folder, filename)

    if os.path.exists(filepath):
        ans = input(f"File exists: {filename}. Overwrite? (y/n): ").strip().lower()
        if ans != 'y':
            print("Skipped saving.")
            return False

    header = (
        f"# Clinical Note - {patient_name.replace('_', ' ')}\n"
        f"**Encounter Date**: {note_date}\n"
        f"**Generated**: {timestamp}\n\n"
        f"---\n\n"
    )
    final = header + clipboard_text

    try:
        os.makedirs(save_folder, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final)
        print(f"Saved: {filename}")
        print(f"Encounter: {note_date}")
        print(f"Location: {filepath}")

        # --- Auto-insert into Titan_Lite DB (single, authoritative place) ---
        try:
            drop_note_py = os.path.join(TITAN_ROOT, "drop_note.py")
            r = subprocess.run(
                [sys.executable, drop_note_py, HANDLE_INSERT, filepath],
                capture_output=True, text=True, check=True
            )
            print(f"[Titan_Lite] Insert OK → {HANDLE_INSERT} | {os.path.basename(filepath)}")
            if r.stdout.strip():
                print(r.stdout.strip())
            if r.stderr.strip():
                print(r.stderr.strip())
        except subprocess.CalledProcessError as e:
            print(f"[Titan_Lite] Insert FAILED: {e}\n{e.stderr or ''}")
        except Exception as e:
            print(f"[Titan_Lite] Insert error: {e}")

        return True
    except Exception as e:
        print(f"Error saving: {e}")
        return False

def main():
    print("SOAP Note Copier started.")
    save_folder = choose_save_folder()
    print(f"Save folder: {save_folder}")
    print("Monitoring clipboard for SOAP notes. Ctrl+C to stop.\n")

    last_clipboard = ""
    try:
        while True:
            try:
                current = pyperclip.paste()
                if current and current != last_clipboard:
                    if process_soap_note(current, save_folder):
                        last_clipboard = current
                        print("\nMonitoring clipboard again...")
                time.sleep(CHECK_INTERVAL)
            except Exception as e:
                print(f"Runtime error: {e}")
                time.sleep(CHECK_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopped.")

if __name__ == "__main__":
    main()
