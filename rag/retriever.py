from rag.loader import build_vector_store
from config import TOP_K_RESULTS

_vector_store = None

def get_vector_store():
    """Singleton — load vector store once per app session."""
    global _vector_store
    if _vector_store is None:
        _vector_store = build_vector_store()
    return _vector_store

def retrieve_context(query: str, k: int = TOP_K_RESULTS) -> str:
    """
    Retrieve top-k relevant document chunks for a given symptom query.
    Returns a formatted string to inject into the LLM prompt.
    """
    try:
        vs = get_vector_store()
        results = vs.similarity_search(query, k=k)

        if not results:
            return ""

        context_parts = []
        for i, doc in enumerate(results, 1):
            source = doc.metadata.get("source", "health document")
            source_type = doc.metadata.get("source_type", "")
            context_parts.append(
                f"[Source {i} ({source})]: {doc.page_content.strip()}"
            )

        return "\n\n".join(context_parts)

    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return ""
