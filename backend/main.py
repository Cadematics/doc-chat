import os
import shutil
import chromadb
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.postprocessor.cohere_rerank import CohereRerank
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

from ingest import ingest_documents_async, delete_document, BASE_DIR, DOCS_DIR, STORAGE_DIR


load_dotenv(BASE_DIR / "backend" / ".env")

app = FastAPI(title="Real Estate Disclosure RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


def build_query_engine():
    docstore_path = STORAGE_DIR / "docstore.json"
    if not docstore_path.exists():
        raise HTTPException(
            status_code=400,
            detail="No indexed documents found. Run ingest.py or upload a PDF first.",
        )

    db = chromadb.PersistentClient(path=str(STORAGE_DIR / "chroma_db"))
    chroma_collection = db.get_or_create_collection("real_estate_disclosures")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        persist_dir=str(STORAGE_DIR),
    )

    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    index = VectorStoreIndex.from_vector_store(
        vector_store,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    base_retriever = index.as_retriever(similarity_top_k=15)
    retriever = AutoMergingRetriever(base_retriever, storage_context, verbose=False)
    reranker = CohereRerank(api_key=os.getenv("COHERE_API_KEY"), top_n=4)
    llm = OpenAI(model="gpt-4o", temperature=0.0)

    return RetrieverQueryEngine.from_args(
        retriever,
        node_postprocessors=[reranker],
        llm=llm,
    )


@app.get("/documents")
def list_documents():
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    pdfs = sorted([f.name for f in DOCS_DIR.glob("*.pdf")])
    return {"documents": pdfs}


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = DOCS_DIR / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    pages_indexed = await ingest_documents_async(target_files=[dest_path])
    return {
        "status": "indexed",
        "file_name": file.filename,
        "pages_indexed": pages_indexed,
    }


@app.post("/ask")
def ask_question(req: QueryRequest):
    engine = build_query_engine()
    grounded_prompt = (
        "You are a senior real estate transaction and disclosure analyst.\n"
        "Answer the question SOLELY using the retrieved context.\n"
        "Strict Rules:\n"
        "1. Cite the exact Document Name and Page Number for every factual statement.\n"
        "2. Quote the exact text, table row, or checkbox state ([X] Yes / [ ] No) that supports your answer.\n"
        "3. If the answer is not explicitly present in the retrieved context, respond ONLY with: "
        "'Information not found in the provided disclosure documents.' Do not guess or extrapolate.\n\n"
        f"Question: {req.question}"
    )

    response = engine.query(grounded_prompt)

    citations = []
    for node in response.source_nodes:
        citations.append(
            {
                "file_name": node.metadata.get("file_name", "Unknown"),
                "page_number": node.metadata.get("page_number", "?"),
                "score": round(node.score, 3) if node.score is not None else None,
                "snippet": node.text,
            }
        )

    return {"answer": str(response), "citations": citations}




@app.delete("/documents/{file_name}")
def remove_document(file_name: str):
    # Prevent path traversal attacks
    safe_name = Path(file_name).name
    result = delete_document(safe_name)
    if not result["file_removed"] and result["deleted_vectors"] == 0 and result["deleted_docstore_nodes"] == 0:
        raise HTTPException(status_code=404, detail=f"Document '{safe_name}' not found.")
    return {"status": "deleted", **result}




