import os
from dotenv import load_dotenv

load_dotenv()

# LLM settings
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "llama3-8b-8192")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# App settings
APP_TITLE = os.getenv("APP_TITLE", "BD Health Assistant")
APP_ICON = "🏥"

# RAG settings
CHROMA_DB_PATH = "data/chroma_db"
DOCS_PATH = "data/docs"
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 64
TOP_K_RESULTS = 5

# Urgency levels
URGENCY_LOW = "low"
URGENCY_MEDIUM = "medium"
URGENCY_HIGH = "high"
URGENCY_EMERGENCY = "emergency"

# Bangladesh healthcare tiers
FACILITY_TIERS = {
    "community_clinic": "Community Clinic (free, nearest)",
    "upazila": "Upazila Health Complex (free government)",
    "district": "District Hospital (government)",
    "medical_college": "Medical College Hospital (specialized)",
    "emergency": "Emergency — call 999 or go to nearest hospital immediately"
}
