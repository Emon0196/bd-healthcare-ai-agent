from config import EMBEDDING_MODEL

def get_embeddings():
    """
    Returns multilingual sentence-transformer embeddings.
    Supports both Bengali and English — critical for this project.
    Model: paraphrase-multilingual-MiniLM-L12-v2 (free, runs locally)
    """
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
        except ImportError:
            raise ImportError(
                "Could not import HuggingFaceEmbeddings. "
                "Make sure langchain-community or langchain-huggingface is installed."
            )
            
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
