import os
import re
import shutil
import chromadb
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from llama_index.core import VectorStoreIndex, StorageContext, PromptTemplate
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.storage.docstore import SimpleDocumentStore
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

MIN_RELEVANCE_SCORE = 0.02

QA_PROMPT = PromptTemplate(
    "You are a senior real estate transaction and disclosure analyst.\n"
    "Context information from the indexed documents is below:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given ONLY the context information above and not prior knowledge, answer the query.\n"
    "Rules:\n"
    "1. Synthesize all relevant facts available in the context, even if the document only contains partial details (such as a recorded notice or summary clause) rather than a full narrative.\n"
    "2. Cite the exact Document Name and Page Number for every factual statement.\n"
    "3. Quote the exact text, table row, or checkbox state ([X] Yes / [ ] No) that supports your answer.\n"
    "4. ONLY if zero relevant facts exist in the context above, respond with: "
    "'Information not found in the provided disclosure documents.'\n\n"
    "Query: {query_str}\n"
    "Answer: "
)


class ChatMessage(BaseModel):
    role: str
    content: str


class QueryRequest(BaseModel):
    question: str
    chat_history: list[ChatMessage] = []


def get_indexed_filenames() -> set[str]:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    return {f.name for f in DOCS_DIR.glob("*.pdf")}


def rewrite_query_with_history(question: str, chat_history: list[ChatMessage]) -> str:
    """Resolve pronouns/references ('the case', 'it', 'the whole story') into a standalone search query."""
    if not chat_history:
        return question

    history_text = "\n".join(
        f"{m.role.upper()}: {m.content[:600]}" for m in chat_history[-4:]
    )
    llm = OpenAI(model="gpt-4o", temperature=0.0)
    condense_prompt = (
        "Given the following conversation history and a follow-up question, rewrite the follow-up question "
        "into a clear, standalone search query that explicitly names the specific subject, person, case number, "
        "or item being discussed. Do NOT answer the question and do NOT add facts not present in the history.\n\n"
        f"Conversation History:\n{history_text}\n\n"
        f"Follow-up Question: {question}\n"
        "Standalone Question:"
    )
    rewritten = str(llm.complete(condense_prompt)).strip()
    return rewritten or question


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

    base_retriever = index.as_retriever(similarity_top_k=20)
    retriever = AutoMergingRetriever(base_retriever, storage_context, verbose=False)
    reranker = CohereRerank(api_key=os.getenv("COHERE_API_KEY"), top_n=4)
    llm = OpenAI(model="gpt-4o", temperature=0.0)

    return RetrieverQueryEngine.from_args(
        retriever,
        node_postprocessors=[reranker],
        text_qa_template=QA_PROMPT,
        llm=llm,
    )


@app.get("/documents")
def list_documents():
    return {"documents": sorted(get_indexed_filenames())}


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


@app.delete("/documents/{file_name}")
def remove_document(file_name: str):
    safe_name = Path(file_name).name
    result = delete_document(safe_name)
    if not result["file_removed"] and result["deleted_vectors"] == 0 and result["deleted_docstore_nodes"] == 0:
        raise HTTPException(status_code=404, detail=f"Document '{safe_name}' not found.")
    return {"status": "deleted", **result}


@app.post("/ask")
def ask_question(req: QueryRequest):
    indexed_files = sorted(get_indexed_filenames())
    if not indexed_files:
        return {
            "answer": "There are currently no documents in the database. Please upload a PDF first.",
            "citations": [],
        }

    # 1. Check if the user explicitly referenced a .pdf file that is not in the database
    mentioned_pdfs = re.findall(r"[\w\-\.\(\)]+\.pdf", req.question, flags=re.IGNORECASE)
    indexed_lower = {name.lower(): name for name in indexed_files}
    missing_pdfs = [pdf for pdf in mentioned_pdfs if pdf.lower() not in indexed_lower]

    if missing_pdfs:
        missing_list = ", ".join(f"`{m}`" for m in missing_pdfs)
        return {
            "answer": f"The document {missing_list} is not in the database, so I have no access to it.",
            "citations": [],
        }

    # 2. Rewrite follow-up queries using recent conversation history
    standalone_question = rewrite_query_with_history(req.question, req.chat_history)
    q_lower = standalone_question.strip().lower()

    # 3. Handle metadata questions about what files are in the database
    if re.search(
        r"\b(names?|list|which|what|show|how many)\b.*\b(documents?|files?|pdfs?|uploaded|database|indexed)\b",
        q_lower,
    ) and not re.search(r"\b(about|summary|summarize|inside|say|mention|content|details)\b", q_lower):
        doc_list = "\n".join(f"- `{name}`" for name in indexed_files)
        return {
            "answer": f"There {'is' if len(indexed_files) == 1 else 'are'} currently **{len(indexed_files)}** indexed document(s) in the database:\n\n{doc_list}",
            "citations": [],
        }

    # 4. Handle broad document overview/summary requests by reading the opening pages directly
    if re.search(r"\b(tell me about (the |this )?document|summarize (the |this )?document|what is this document|overview of (the )?document)\b", q_lower):
        docstore_path = STORAGE_DIR / "docstore.json"
        if docstore_path.exists():
            docstore = SimpleDocumentStore.from_persist_path(str(docstore_path))
            # Pick longest parent node per (file_name, page_number) for pages 1-3
            opening_pages = {}
            for node in docstore.docs.values():
                fname = node.metadata.get("file_name")
                pnum = node.metadata.get("page_number", 999)
                if fname in indexed_files and isinstance(pnum, int) and pnum <= 3:
                    key = (fname, pnum)
                    if key not in opening_pages or len(node.text) > len(opening_pages[key].text):
                        opening_pages[key] = node

            sorted_nodes = [opening_pages[k] for k in sorted(opening_pages.keys())]
            if sorted_nodes:
                context_block = "\n\n---\n\n".join(
                    f"[{n.metadata['file_name']} - Page {n.metadata['page_number']}]\n{n.text}"
                    for n in sorted_nodes
                )
                llm = OpenAI(model="gpt-4o", temperature=0.0)
                summary_prompt = (
                    "Provide a clear, structured executive overview of the indexed real estate document(s) "
                    "based ONLY on the opening pages below. Cite the exact Document Name and Page Number.\n\n"
                    f"{context_block}"
                )
                summary_resp = llm.complete(summary_prompt)
                citations = [
                    {
                        "file_name": n.metadata.get("file_name", "Unknown"),
                        "page_number": n.metadata.get("page_number", "?"),
                        "score": 1.0,
                        "snippet": n.text,
                    }
                    for n in sorted_nodes[:4]
                ]
                return {"answer": str(summary_resp).strip(), "citations": citations}

    # 5. Standard targeted RAG retrieval + Cohere reranking
    engine = build_query_engine()
    response = engine.query(standalone_question)

    answer_text = str(response).strip()
    if not response.source_nodes or "information not found in the provided disclosure documents" in answer_text.lower():
        return {
            "answer": "Information not found in the provided disclosure documents.",
            "citations": [],
        }

    # Keep top reranked source nodes (deduplicated by file_name + page_number)
    seen_pages = set()
    citations = []
    for node in response.source_nodes:
        fname = node.metadata.get("file_name", "Unknown")
        pnum = node.metadata.get("page_number", "?")
        key = (fname, pnum)
        if key in seen_pages:
            continue
        seen_pages.add(key)

        try:
            score_val = round(float(node.score), 3) if node.score is not None else None
        except (TypeError, ValueError):
            score_val = None

        citations.append(
            {
                "file_name": fname,
                "page_number": pnum,
                "score": score_val,
                "snippet": node.text,
            }
        )

    return {"answer": answer_text, "citations": citations}