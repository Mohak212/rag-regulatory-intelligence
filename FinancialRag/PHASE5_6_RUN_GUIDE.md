# Phase 5 and 6 Run Guide

This merged project root is `FinancialRag`.

## What Was Merged

- `FinancialRag.zip` supplies `data/raw`, `data/processed`, and `data/chunks`.
- `code.zip` supplies the phase 2, 3, and 4 scripts, now copied into this root.
- `vector_store.zip` supplies the Chroma index, now copied to `data/vector_store`.

The phase 4 index metadata reports 5,954 indexed chunks in the `regulatory_chunks` collection using `BAAI/bge-base-en-v1.5`.

## Install

```powershell
python -m pip install -r requirements.txt
```

## Phase 5: Retrieval

Run hybrid retrieval with semantic search plus built-in BM25 keyword search:

```powershell
python phase5_6_rag.py "What is the rating process for credit rating agencies?" --domain SEBI --no-llm
```

Domain filters:

- `all`
- `SEBI`
- `RBI`
- `IncomeTax`

## Phase 6: LLM Answer Generation

Free local Ollama mode:

```powershell
python phase5_6_rag.py "What is the rating process for credit rating agencies?" --domain SEBI --provider ollama --ollama-model qwen2.5-coder:7b
```

This uses your local Ollama server at `http://localhost:11434` and does not require an OpenAI API key.

If local generation is slow, reduce retrieved context or increase the wait:

```powershell
python phase5_6_rag.py "What are the main rules for P2P lending platforms?" --domain RBI --top-k 2 --provider ollama --ollama-model qwen2.5-coder:7b --ollama-timeout 900
```

Free offline test mode:

```powershell
python phase5_6_rag.py "What does RBI say about P2P lending?" --domain RBI --mock-llm
```

This tests the Phase 6 citation and answer path without calling a paid API. It is extractive and simpler than a real LLM.

Set an OpenAI key, then run without `--no-llm`:

```powershell
$env:OPENAI_API_KEY="your_key_here"
python phase5_6_rag.py "What does RBI say about P2P lending?" --domain RBI
```

The answer prompt instructs the model to answer only from retrieved context and cite source labels, circular numbers, and dates.

## Phase 7: API and Frontend

Run the FastAPI app:

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

The UI uses Ollama by default for free local testing. Switch the provider to OpenAI after setting `OPENAI_API_KEY`.

The UI opens with a language preference screen and supports English, Hindi, Bengali, Gujarati, Kannada, Malayalam, Marathi, Odia, Punjabi, Tamil, and Telugu. The selected language is used for answer generation and voice input. Non-English questions are translated to English for retrieval, then answered in the selected language.

Voice input uses the browser Web Speech API, so it works best in Chrome or Edge and may ask for microphone permission.

## Optional Hugging Face RBI Enrichment

This is intentionally separate from the original vector store.

```powershell
python hf_enrichment.py all --assignment-limit 2000 --lirus-limit 1710
```

It writes:

- `data/hf_experimental/raw`
- `data/hf_experimental/chunks`
- `data/vector_store_hf_experimental`

To test from the CLI:

```powershell
python phase5_6_rag.py "What is the purpose of Prompt Corrective Action?" --domain RBI --top-k 5 --include-hf-experimental --no-llm
```

In the web UI, enable `Include Hugging Face RBI QA experimental data`. HF results are tagged separately and are not treated as official RBI PDF sources.
