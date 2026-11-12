Markdown
# doc-chat

A zero-hallucination RAG web app for chatting with complex, multi-hundred-page PDFs (real estate disclosures, inspection reports, contracts, and technical manuals) with exact page-level citations.

## Features

- **Layout-Aware PDF Parsing:** Uses LlamaCloud to extract clean Markdown while preserving tables and checkbox states (`[X] Yes` / `[ ] No`).
- **Parent-Child Retrieval:** Indexes small child chunks (`128` / `512` tokens) in ChromaDB for high-precision search, then retrieves full `2048`-token parent sections via LlamaIndex `AutoMergingRetriever`.
- **Cross-Encoder Reranking:** Uses Cohere Rerank to filter out noisy matches before synthesis.
- **Grounded Citations:** Forces GPT-4o to cite exact file names, page numbers, and verbatim quotes—refusing to guess when information is not in the documents.
- **Document Management:** Upload new PDFs, query across indexed files, or remove documents from both the vector database and local storage.

## Tech Stack

- **Backend:** Python, FastAPI, LlamaIndex, LlamaCloud, ChromaDB, Cohere, OpenAI
- **Frontend:** Streamlit

## Quickstart

### 1. Setup Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
2. Add API Keys
Create backend/.env and add your keys:
```


Code snippet
```bash
OPENAI_API_KEY=your_openai_key
LLAMA_CLOUD_API_KEY=your_llamacloud_key
COHERE_API_KEY=your_cohere_key
```

3. Index PDFs & Run the App
Place your PDFs inside docs/, then run:


# 1. Parse and index documents
```bash
cd backend && python ingest.py
```
# 2. Start the FastAPI server (Terminal 1)
```bash
uvicorn main:app --reload --port 8000
```


# 3. Start the Streamlit UI (Terminal 2)
```bash
cd ../frontend && streamlit run app.py
```

Open http://localhost:8501 in your browser to start asking questions.
