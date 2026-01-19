import os
from typing import List
from dotenv import load_dotenv
load_dotenv()

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

RAG_DOCS_DIR = os.getenv("RAG_DOCS_DIR", ".onboarding-llm/rag_docs")
RAG_INDEX_DIR = os.getenv("RAG_INDEX_DIR", ".onboarding-llm/rag_index")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def _load_docs() -> List:
    docs = []
    print("RAG DOC FILES:", os.listdir(RAG_DOCS_DIR))
    if not os.path.exists(RAG_DOCS_DIR):
        return docs

    for fname in os.listdir(RAG_DOCS_DIR):
        path = os.path.join(RAG_DOCS_DIR, fname)
        if fname.lower().endswith(".pdf"):
            docs.extend(PyPDFLoader(path).load())
        elif fname.lower().endswith(".txt"):
            docs.extend(TextLoader(path, encoding="utf-8").load())
    return docs


def _embeddings():
    # Local embeddings → no 429 → public-safe
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


def build_or_load_vectorstore() -> FAISS:
    index_path = os.path.join(RAG_INDEX_DIR, "faiss_index")
    emb = _embeddings()

    if os.path.exists(index_path):
        return FAISS.load_local(index_path, emb, allow_dangerous_deserialization=True)

    docs = _load_docs()
    print("DOCS LOADED:", [(d.metadata.get("source"), len(d.page_content or "")) for d in docs])
    if not docs:
        raise RuntimeError(f"No docs found in {RAG_DOCS_DIR}. Put PDFs there.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=150)
    chunks = splitter.split_documents(docs)

    vs = FAISS.from_documents(chunks, emb)
    os.makedirs(RAG_INDEX_DIR, exist_ok=True)
    vs.save_local(index_path)
    return vs


def retrieve(query: str, k: int = 4):
    vs = build_or_load_vectorstore()
    docs = vs.similarity_search(query, k=k)
    print("RAG QUERY:", query)
    print("RAG FILES:", os.listdir(RAG_DOCS_DIR))
    # normalize metadata for citations
    for d in docs:
        meta = d.metadata or {}
        src = meta.get("source", "unknown")
        meta["source_name"] = os.path.basename(src)
        meta["page"] = meta.get("page", None)
        d.metadata = meta
    print("RAG HIT:", [d.metadata["source_name"] for d in docs])
    return docs
