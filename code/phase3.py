import json
import os
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Directory Setup based on your project structure [cite: 24, 31]
PROCESSED_BASE_DIR = Path("data/processed")
CHUNKS_BASE_DIR = Path("data/chunks")

def run_phase_3_chunking():
    # Initialize the recursive splitter 
    # We use ~1500 characters to aim for 300-500 tokens with 10% overlap
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200,
        separators=["\n\n", "\n", ".", " "],
        length_function=len,
    )

    for domain in ["rbi", "sebi"]:
        source_path = PROCESSED_BASE_DIR / domain
        target_path = CHUNKS_BASE_DIR / domain
        target_path.mkdir(parents=True, exist_ok=True)

        print(f"🚀 Starting Chunking for {domain.upper()}...")

        for json_file in source_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)

                # Extract the cleaned content from Phase 2
                full_text = doc_data.get("content", "")
                metadata = doc_data.get("metadata", {})

                if not full_text:
                    print(f"⚠️ Skipping {json_file.name}: No content found.")
                    continue

                # Perform the split 
                chunks = text_splitter.split_text(full_text)

                # Package each chunk with inherited metadata [cite: 89]
                chunked_objects = []
                for i, chunk_text in enumerate(chunks):
                    chunk_entry = {
                        "chunk_id": f"{domain}_{metadata.get('circular_number', 'unknown')}_{i}",
                        "text": chunk_text,
                        "metadata": metadata  # Metadata inheritance 
                    }
                    chunked_objects.append(chunk_entry)

                # Save the chunked list
                output_filename = f"chunks_{json_file.name}"
                with open(target_path / output_filename, 'w', encoding='utf-8') as f:
                    json.dump(chunked_objects, f, indent=2, ensure_ascii=False)

                print(f"✅ Created {len(chunks)} chunks for {json_file.name}")

            except Exception as e:
                print(f"❌ Failed to chunk {json_file.name}: {e}")

if __name__ == "__main__":
    run_phase_3_chunking()