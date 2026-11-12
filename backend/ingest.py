import os
import asyncio
import chromadb
from pathlib import Path
from dotenv import load_dotenv
from llama_cloud import AsyncLlamaCloud
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.core.node_parser import HierarchicalNodeParser, get_leaf_nodes
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_DIR = BASE_DIR / "docs"
STORAGE_DIR = BASE_DIR / "storage"
load_dotenv(BASE_DIR / "backend" / ".env")


async def _parse_single_pdf(client: AsyncLlamaCloud, pdf_path: Path) -> list[Document]:
    print(f"Uploading and parsing {pdf_path.name} with LlamaCloud...")
    uploaded_file = await client.files.create(file=pdf_path, purpose="parse")
    result = await client.parsing.parse(
        file_id=uploaded_file.id,
        tier="agentic",
        version="latest",
        expand=["markdown"],
    )

    docs = []
    if result.markdown and result.markdown.pages:
        for idx, page in enumerate(result.markdown.pages, start=1):
            page_num = getattr(page, "page_number", None) or getattr(page, "page", idx)
            md_text = getattr(page, "markdown", "") or ""
            if md_text.strip():
                docs.append(
                    Document(
                        text=md_text,
                        metadata={
                            "file_name": pdf_path.name,
                            "page_number": page_num,
                        },
                    )
                )
    return docs


async def ingest_documents_async(target_files: list[Path] | None = None) -> int:
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    files = target_files if target_files else sorted(DOCS_DIR.glob("*.pdf"))
    if not files:
        print("No PDF files found to ingest.")
        return 0

    all_documents: list[Document] = []
    async with AsyncLlamaCloud(api_key=os.getenv("LLAMA_CLOUD_API_KEY")) as client:
        for pdf_path in files:
            parsed_docs = await _parse_single_pdf(client, pdf_path)
            all_documents.extend(parsed_docs)

    if not all_documents:
        return 0

    # Hierarchical chunking: 2048-token parents for full context, 512/128-token children for precision
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[2048, 512, 128])
    nodes = node_parser.get_nodes_from_documents(all_documents)
    leaf_nodes = get_leaf_nodes(nodes)

    db = chromadb.PersistentClient(path=str(STORAGE_DIR / "chroma_db"))
    chroma_collection = db.get_or_create_collection("real_estate_disclosures")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    docstore_path = STORAGE_DIR / "docstore.json"
    docstore = (
        SimpleDocumentStore.from_persist_path(str(docstore_path))
        if docstore_path.exists()
        else SimpleDocumentStore()
    )
    docstore.add_documents(nodes)

    storage_context = StorageContext.from_defaults(
        vector_store=vector_store,
        docstore=docstore,
    )

    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    VectorStoreIndex(
        leaf_nodes,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    storage_context.persist(persist_dir=str(STORAGE_DIR))
    print(f"Successfully indexed {len(all_documents)} pages across {len(files)} PDF(s).")
    return len(all_documents)


def ingest_documents(target_files: list[Path] | None = None) -> int:
    return asyncio.run(ingest_documents_async(target_files))


def delete_document(file_name: str) -> dict:
    """Removes a document's vectors from ChromaDB, parent nodes from docstore.json, and raw PDF from docs/."""
    deleted_vectors = 0
    deleted_docstore_nodes = 0

    # 1. Remove leaf embeddings from ChromaDB by metadata filter
    chroma_path = STORAGE_DIR / "chroma_db"
    if chroma_path.exists():
        db = chromadb.PersistentClient(path=str(chroma_path))
        chroma_collection = db.get_or_create_collection("real_estate_disclosures")
        existing = chroma_collection.get(where={"file_name": file_name})
        if existing and existing.get("ids"):
            deleted_vectors = len(existing["ids"])
            chroma_collection.delete(ids=existing["ids"])

    # 2. Remove both parent & child nodes from SimpleDocumentStore
    docstore_path = STORAGE_DIR / "docstore.json"
    if docstore_path.exists():
        docstore = SimpleDocumentStore.from_persist_path(str(docstore_path))
        node_ids_to_delete = [
            node_id
            for node_id, node in docstore.docs.items()
            if node.metadata.get("file_name") == file_name
        ]
        for node_id in node_ids_to_delete:
            docstore.delete_document(node_id)
        deleted_docstore_nodes = len(node_ids_to_delete)
        docstore.persist(persist_path=str(docstore_path))

    # 3. Remove the physical PDF from docs/
    pdf_path = DOCS_DIR / file_name
    file_removed = False
    if pdf_path.exists():
        pdf_path.unlink()
        file_removed = True

    return {
        "file_name": file_name,
        "file_removed": file_removed,
        "deleted_vectors": deleted_vectors,
        "deleted_docstore_nodes": deleted_docstore_nodes,
    }





if __name__ == "__main__":
    ingest_documents()