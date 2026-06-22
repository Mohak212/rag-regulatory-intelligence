"""
RBI Circular — Metadata JSON Generator
========================================
For Mohak — RBI domain

The RBI portal blocks automated downloads (HTTP 403 / Akamai).
This script has TWO modes:

MODE 1 — AUTO-GENERATE JSONs for files you already downloaded manually
         Drop your PDFs into data/raw/rbi/ and run this script.
         It reads each PDF, extracts the circular number and date,
         and creates the metadata JSON automatically.

MODE 2 — OPEN BROWSER TABS for you to download manually
         Run: python generate_rbi_json.py --open-browser
         Opens each circular URL in your browser in batches of 5.
         Save each PDF to data/raw/rbi/, then run MODE 1.

Usage:
    pip install PyMuPDF
    python generate_rbi_json.py                 # MODE 1: generate JSONs
    python generate_rbi_json.py --open-browser  # MODE 2: open browser tabs

Where to find circulars manually:
    Circulars:         https://rbi.org.in/scripts/bs_circularindexdisplay.aspx
    All Notifications: https://rbi.org.in/Scripts/NotificationUser.aspx
    Master Directions: https://rbi.org.in/scripts/bs_viewmastercirculars.aspx
"""

import os
import re
import json
import sys
import time
import webbrowser
from datetime import date

import fitz  # PyMuPDF

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
SAVE_DIR = "data/raw/rbi"
TODAY = date.today().isoformat()

# ─────────────────────────────────────────────
# KNOWN RBI CIRCULAR & MASTER DIRECTION URLS
# Source: rbi.org.in — open these in browser and save as PDF
# RBI circular number format: RBI/YYYY-YY/NUM
# ─────────────────────────────────────────────
CIRCULAR_URLS = [

    # ── MASTER DIRECTIONS (most comprehensive — download these first) ──────
    # Master Direction on KYC
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11566",
    # Master Direction on Fraud Risk Management
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12699",
    # Master Direction on Interest Rate on Deposits
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10184",
    # Master Direction on Loans and Advances
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10916",
    # Master Direction on Priority Sector Lending
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11959",
    # Master Direction on NBFC
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11070",
    # Master Direction on Prepaid Payment Instruments
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12156",
    # Master Direction on Peer-to-Peer Lending
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=11137",
    # Master Direction on Digital Payment Security Controls
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12158",
    # Master Direction on Credit Card and Debit Card
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12300",
    # Master Direction on Outsourcing of IT Services
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=12382",
    # Master Direction on Cyber Security Framework
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10435",
    # Master Direction on Foreign Investment in India
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10989",
    # Master Direction on Export of Goods and Services
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10127",
    # Master Direction on Liberalised Remittance Scheme
    "https://rbi.org.in/Scripts/BS_ViewMasDirections.aspx?id=10192",

    # ── CIRCULARS 2025 ────────────────────────────────────────────────────
    # Lending Against Gold and Silver Collateral Directions 2025
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12746&Mode=0",
    # Asset Liability Management Directions 2025
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12749&Mode=0",
    # Penal Interest on CRR and SLR shortfall
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12737&Mode=0",
    # Large Exposures Framework amendment
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12740&Mode=0",
    # Digital Payments Index March 2025
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12734&Mode=0",
    # AIF Investment Norms for Lenders
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12720&Mode=0",
    # Liquidity Adjustment Facility rate change
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12715&Mode=0",

    # ── CIRCULARS 2024 ────────────────────────────────────────────────────
    # Credit Card issuance directions
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12697&Mode=0",
    # Margining for non-centrally cleared OTC derivatives
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12693&Mode=0",
    # Review of Risk Weights for HFCs
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12671&Mode=0",
    # Frequency of reporting to Credit Information Companies
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12660&Mode=0",
    # Processing of e-mandates for recurring transactions
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12640&Mode=0",
    # Regulatory Principles for Model Risk Management in Credit
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12617&Mode=0",
    # Modified Interest Subvention Scheme for KCC 2024-25
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12607&Mode=0",
    # Review of Qualifying Assets Criteria
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12590&Mode=0",
    # NDS-OM Access Criteria Directions 2024
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12560&Mode=0",
    # BBPS update for bill payments
    "https://rbi.org.in/Scripts/NotificationUser.aspx?Id=12543&Mode=0",
]


# ─────────────────────────────────────────────
# PDF TEXT EXTRACTION HELPERS
# ─────────────────────────────────────────────

def extract_text_from_pdf(filepath):
    """Extract all text from a PDF using PyMuPDF."""
    try:
        doc = fitz.open(filepath)
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        return full_text.strip()
    except Exception as e:
        print(f"   ⚠️  Could not read PDF: {e}")
        return ""


def is_scanned(text):
    """Return True if PDF had no extractable text."""
    return len(text.strip()) < 50


def extract_circular_number(text):
    """
    Extract RBI circular number from PDF text.
    RBI format: RBI/YYYY-YY/NUM  e.g. RBI/2024-25/45
    Also handles Master Direction numbers.
    """
    # Standard circular number: RBI/2024-25/45
    match = re.search(r"RBI/(\d{4}-\d{2,4}/\d+)", text, re.IGNORECASE)
    if match:
        return f"RBI/{match.group(1)}"

    # Master Direction reference
    match2 = re.search(r"(Master\s+Direction[^\n]{0,80})", text, re.IGNORECASE)
    if match2:
        return match2.group(1).strip()[:80]

    # Master Circular reference
    match3 = re.search(r"(Master\s+Circular[^\n]{0,80})", text, re.IGNORECASE)
    if match3:
        return match3.group(1).strip()[:80]

    return ""   # not found — fill manually


def extract_date(text):
    """
    Extract the date from RBI circular text.
    Looks for: "April 11, 2025" / "11 April 2025" / "April 11, 2025"
    """
    months = {
        "january": "01", "february": "02", "march": "03", "april": "04",
        "may": "05", "june": "06", "july": "07", "august": "08",
        "september": "09", "october": "10", "november": "11", "december": "12"
    }

    # Pattern: "April 11, 2025" or "April 11 2025"
    pattern1 = r"(" + "|".join(months.keys()) + r")\s+(\d{1,2})[,\s]+(\d{4})"
    match = re.search(pattern1, text, re.IGNORECASE)
    if match:
        month = months[match.group(1).lower()]
        day = match.group(2).zfill(2)
        year = match.group(3)
        return f"{year}-{month}-{day}"

    # Pattern: "11 April, 2025" or "11th April 2025"
    pattern2 = r"(\d{1,2})(?:st|nd|rd|th)?\s+(" + "|".join(months.keys()) + r")[,\s]+(\d{4})"
    match2 = re.search(pattern2, text, re.IGNORECASE)
    if match2:
        day = match2.group(1).zfill(2)
        month = months[match2.group(2).lower()]
        year = match2.group(3)
        return f"{year}-{month}-{day}"

    # DD/MM/YYYY or DD-MM-YYYY
    match3 = re.search(r"(\d{2})[/-](\d{2})[/-](\d{4})", text)
    if match3:
        return f"{match3.group(3)}-{match3.group(2)}-{match3.group(1)}"

    return ""   # not found — fill manually


def detect_document_type(text, filename):
    """Detect whether this is a Master Direction, Master Circular, or regular Circular."""
    text_lower = text.lower()
    filename_lower = filename.lower()

    if "master direction" in text_lower or "master direction" in filename_lower:
        return "Master Direction"
    elif "master circular" in text_lower or "master circular" in filename_lower:
        return "Master Circular"
    else:
        return "Circular"


def source_url_from_filename(filename):
    """Return the RBI notifications listing page as default source."""
    return "https://rbi.org.in/Scripts/NotificationUser.aspx"


# ─────────────────────────────────────────────
# MODE 1 — Generate JSONs for existing PDFs
# ─────────────────────────────────────────────

def generate_jsons_for_existing_pdfs():
    """
    Scan data/raw/rbi/ for PDFs without a JSON.
    Extract circular number, date, and doc type from text.
    Create metadata JSON for each.
    """
    print("=" * 60)
    print("  MODE 1 — JSON Generator for Downloaded RBI PDFs")
    print("=" * 60)

    os.makedirs(SAVE_DIR, exist_ok=True)
    files = sorted(os.listdir(SAVE_DIR))
    pdfs = [f for f in files if f.endswith(".pdf")]

    if not pdfs:
        print(f"\n⚠️  No PDFs found in {SAVE_DIR}/")
        print("   Download some circulars first (run with --open-browser),")
        print("   save them to data/raw/rbi/, then run this script again.\n")
        return

    print(f"\nFound {len(pdfs)} PDFs. Generating JSONs...\n")

    created = 0
    skipped = 0
    needs_review = []

    for pdf_file in pdfs:
        json_file = pdf_file.replace(".pdf", ".json")
        pdf_path = os.path.join(SAVE_DIR, pdf_file)
        json_path = os.path.join(SAVE_DIR, json_file)

        print(f"📄 {pdf_file}")

        if os.path.exists(json_path):
            print(f"   ⏭️  JSON already exists, skipping.\n")
            skipped += 1
            continue

        # Extract text
        text = extract_text_from_pdf(pdf_path)
        scanned = is_scanned(text)

        if scanned:
            print(f"   ⚠️  Scanned PDF — flagging is_scanned: true")
            circular_number = ""
            date_str = ""
            doc_type = "Circular"
        else:
            circular_number = extract_circular_number(text)
            date_str = extract_date(text)
            doc_type = detect_document_type(text, pdf_file)
            print(f"   🔍 Type:            {doc_type}")
            print(f"   🔍 Circular number: {circular_number or '(not found — fill manually)'}")
            print(f"   🔍 Date:            {date_str or '(not found — fill manually)'}")

        needs_manual = not circular_number or not date_str
        note = "REVIEW: circular_number or date missing — fill manually" if needs_manual else ""

        metadata = {
            "filename": pdf_file,
            "domain": "RBI",
            "document_type": doc_type,
            "circular_number": circular_number,
            "date": date_str,
            "source_url": source_url_from_filename(pdf_file),
            "downloaded_at": TODAY,
            "is_scanned": scanned,
            "is_english": True,
            "notes": note
        }

        with open(json_path, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"   ✅ JSON created: {json_file}\n")
        created += 1

        if needs_manual:
            needs_review.append(json_file)

    print("=" * 60)
    print(f"  Done! Created: {created} | Skipped: {skipped}")
    print("=" * 60)

    if needs_review:
        print(f"\n⚠️  {len(needs_review)} JSON(s) need manual review:")
        for jf in needs_review:
            print(f"   Open and fill in missing fields: {jf}")


# ─────────────────────────────────────────────
# MODE 2 — Open browser tabs
# ─────────────────────────────────────────────

def open_browser_tabs():
    """
    Open RBI circular URLs in batches of 5 in the default browser.
    User saves each PDF to data/raw/rbi/ manually.

    NOTE: RBI pages open as HTML. To save as PDF:
    - In Chrome/Edge: press Ctrl+P → Save as PDF → Save
    - Or use browser's Print → Save as PDF
    """
    print("=" * 60)
    print("  MODE 2 — Open RBI Circular URLs in Browser")
    print("=" * 60)
    print(f"\nThis will open {len(CIRCULAR_URLS)} URLs in your browser.")
    print(f"Save folder: {os.path.abspath(SAVE_DIR)}\n")

    print("⚠️  IMPORTANT — RBI pages open as HTML, not direct PDFs.")
    print("   To save as PDF:")
    print("   Chrome/Edge → Ctrl+P → Destination: Save as PDF → Save")
    print("   Name the file: RBI_circular_YYYY_MM_DD_description.pdf\n")

    os.makedirs(SAVE_DIR, exist_ok=True)

    print("Opening in batches of 5 (press Enter for each batch)...\n")

    for i in range(0, len(CIRCULAR_URLS), 5):
        batch = CIRCULAR_URLS[i:i+5]
        print(f"Batch {i//5 + 1}: Opening {len(batch)} tabs...")
        for url in batch:
            print(f"  → {url}")
            webbrowser.open(url)
            time.sleep(0.8)

        if i + 5 < len(CIRCULAR_URLS):
            input("\n  ✅ Save those PDFs, then press Enter for next batch...")

    print(f"\n✅ All URLs opened!")
    print(f"\nOnce all PDFs are saved to {SAVE_DIR}/")
    print("Run:  python generate_rbi_json.py")
    print("to auto-generate all JSON metadata files.\n")

    print("Naming convention reminder:")
    print("  RBI_masterdirection_YYYY_MM_DD_kyc.pdf")
    print("  RBI_circular_YYYY_MM_DD_gold_loans.pdf")
    print("  RBI_circular_YYYY_MM_DD_nbfc_directions.pdf\n")


# ─────────────────────────────────────────────
# VALIDATION
# ─────────────────────────────────────────────

def validate():
    print("\n" + "=" * 60)
    print("  VALIDATION REPORT — RBI")
    print("=" * 60)

    files = os.listdir(SAVE_DIR)
    pdfs = sorted([f for f in files if f.endswith(".pdf")])
    errors = []

    print(f"Total PDFs: {len(pdfs)}\n")

    master_directions = 0
    circulars = 0

    for pdf in pdfs:
        json_file = pdf.replace(".pdf", ".json")
        json_path = os.path.join(SAVE_DIR, json_file)

        if not os.path.exists(json_path):
            errors.append(f"MISSING JSON:      {pdf}")
            continue

        try:
            with open(json_path) as f:
                data = json.load(f)
        except:
            errors.append(f"INVALID JSON:      {json_file}")
            continue

        if data.get("domain") != "RBI":
            errors.append(f"BAD DOMAIN:        {pdf} → '{data.get('domain')}'")
        if not data.get("circular_number"):
            errors.append(f"MISSING CIRC NUM:  {pdf}")
        if not data.get("date"):
            errors.append(f"MISSING DATE:      {pdf}")
        if data.get("is_english") is not True:
            errors.append(f"NOT ENGLISH FLAG:  {pdf} — check is_english field")

        doc_type = data.get("document_type", "")
        if "Master" in doc_type:
            master_directions += 1
        else:
            circulars += 1

    print(f"  Master Directions: {master_directions}")
    print(f"  Circulars:         {circulars}")
    print(f"  Total:             {master_directions + circulars}\n")

    if master_directions < 10:
        print(f"  ⚠️  Recommended: at least 10–15 Master Directions (currently {master_directions})")
    if circulars < 10:
        print(f"  ⚠️  Recommended: at least 10–15 Circulars (currently {circulars})")

    if errors:
        print("\n❌ Issues found:")
        for e in errors:
            print(f"   {e}")
    else:
        print("✅ All checks passed! No missing JSONs, no bad domain values.")
        print(f"   Phase 1 complete for RBI domain.")

    print("=" * 60 + "\n")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    if "--open-browser" in sys.argv:
        open_browser_tabs()
    else:
        generate_jsons_for_existing_pdfs()
        if os.path.exists(SAVE_DIR) and any(f.endswith(".pdf") for f in os.listdir(SAVE_DIR)):
            validate()
