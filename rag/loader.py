import os
import sys

# Force pure-python implementation of Protobuf to avoid descriptor conflict errors on Streamlit Cloud
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

from pathlib import Path

# Add project root to path to allow executing this file directly
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from rag.embeddings import get_embeddings
from config import CHROMA_DB_PATH, DOCS_PATH, CHUNK_SIZE, CHUNK_OVERLAP

def load_documents():
    """Load all PDFs and text files from the docs directory."""
    documents = []
    docs_path = Path(DOCS_PATH)

    if not docs_path.exists():
        print(f"Warning: {DOCS_PATH} does not exist. Creating empty directory.")
        docs_path.mkdir(parents=True, exist_ok=True)
        return documents

    # Load PDFs
    for pdf_file in docs_path.rglob("*.pdf"):
        try:
            loader = PyPDFLoader(str(pdf_file))
            docs = loader.load()
            # Tag each document with its source folder for filtering later
            for doc in docs:
                doc.metadata["source_type"] = pdf_file.parent.name
                doc.metadata["source"] = pdf_file.name
            documents.extend(docs)
            print(f"Loaded: {pdf_file.name} ({len(docs)} pages)")
        except Exception as e:
            print(f"Failed to load {pdf_file.name}: {e}")

    # Load text files
    for txt_file in docs_path.rglob("*.txt"):
        try:
            loader = TextLoader(str(txt_file), encoding="utf-8")
            docs = loader.load()
            for doc in docs:
                doc.metadata["source_type"] = "manual"
                doc.metadata["source"] = txt_file.name
            documents.extend(docs)
            print(f"Loaded: {txt_file.name}")
        except Exception as e:
            print(f"Failed to load {txt_file.name}: {e}")

    print(f"\nTotal documents loaded: {len(documents)}")
    return documents

def split_documents(documents):
    """Split documents into chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ".", "!", "?", ",", " "]
    )
    chunks = splitter.split_documents(documents)
    print(f"Total chunks created: {len(chunks)}")
    return chunks

def build_vector_store(force_rebuild: bool = False):
    """
    Build or load ChromaDB vector store.
    Set force_rebuild=True to re-ingest all documents.
    """
    embeddings = get_embeddings()
    chroma_path = Path(CHROMA_DB_PATH)

    # If DB already exists and we're not forcing rebuild, load it
    if chroma_path.exists() and not force_rebuild:
        print("Loading existing ChromaDB vector store...")
        return Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings
        )

    print("Building new ChromaDB vector store...")
    documents = load_documents()

    if not documents:
        print("No documents found. Vector store will be empty.")
        return Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings
        )

    chunks = split_documents(documents)
    
    # Chroma 0.4.x / 0.5.x handles persist directory initialization
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    # In newer langchain-chroma / chromadb, persistence is automatic.
    # We call persist() only if it exists (for backward compatibility).
    if hasattr(vector_store, "persist"):
        vector_store.persist()
        
    print(f"Vector store built and saved to {CHROMA_DB_PATH}")
    return vector_store

if __name__ == "__main__":
    build_vector_store(force_rebuild=True)
    print("Done. Vector store is ready.")
