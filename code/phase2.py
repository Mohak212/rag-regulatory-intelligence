import os
import json
import fitz  # PyMuPDF
from pathlib import Path

# Paths
RAW_DIR = Path("data/raw/rbi")
PROCESSED_DIR = Path("data/processed/rbi")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def run_rbi_phase_2():
    print("🚀 Starting RBI Extraction...")
    for pdf_file in RAW_DIR.glob("*.pdf"):
        # RBI Format: RBI_circular_2015_11_18_PSL2.pdf
        # Match with JSON of same name
        meta_file = pdf_file.with_suffix(".json")
        
        if not meta_file.exists():
            print(f"❌ Skipping {pdf_file.name}: No metadata JSON found.")
            continue

        try:
            with open(meta_file, 'r') as f:
                metadata = json.load(f)

            # Extraction
            doc = fitz.open(pdf_file)
            content = "".join([page.get_text() for page in doc])
            doc.close()

            # Final RAG structure
            processed_data = {
                "metadata": metadata,
                "content": content.strip()
            }

            output_name = f"processed_{pdf_file.stem}.json"
            with open(PROCESSED_DIR / output_name, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Processed: {pdf_file.name}")
        except Exception as e:
            print(f"⚠️ Error in {pdf_file.name}: {e}")

if __name__ == "__main__":
    run_rbi_phase_2()