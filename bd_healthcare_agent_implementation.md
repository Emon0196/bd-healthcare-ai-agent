# BD Healthcare Symptom Assistant — Complete Implementation Document
> **For:** Google Antigravity Agent Manager
> **Project type:** RAG-based Agentic AI — symptom analysis and care referral
> **Target population:** Bangladesh general public
> **Language:** Python 3.11+
> **Status:** Build phase by phase in order. Do not skip phases.

---

## Agent Instructions (Read First)

You are building a responsible, safe healthcare assistant for the Bangladesh population. This app does **not** prescribe medicine. It analyzes symptoms, provides general health information grounded in Bangladesh-specific medical documents, classifies urgency, and refers users to appropriate healthcare facilities.

Every response the app generates to users **must** include a disclaimer:
> *"This is not medical advice. Please consult a registered MBBS doctor or visit your nearest health facility for diagnosis and treatment."*

Build phase by phase. Each phase is self-contained and testable before moving to the next. After completing each phase, verify it runs without errors before proceeding.

---

## Project Overview

### What this app does
1. User describes symptoms in plain text (Bengali or English)
2. Agent analyzes symptoms using RAG over Bangladesh health documents
3. Agent classifies urgency: low / medium / high / emergency
4. Agent suggests possible conditions (not diagnosis) with educational context
5. Agent refers user to the appropriate healthcare facility tier in Bangladesh

### What this app does NOT do
- Does not prescribe medicine
- Does not diagnose diseases
- Does not replace a doctor
- Does not store personal health data

### Target diseases (Phase 1 scope)
Dengue fever, typhoid, chikungunya, diarrhea, cholera, tuberculosis, malaria, respiratory infections, diabetes symptoms, hypertension symptoms, skin infections, eye infections, worm infestation, jaundice, anemia symptoms.

---

## Final Folder Structure (build toward this)

```
bd_healthcare_agent/
├── app.py                          # Streamlit entry point
├── config.py                       # All settings and constants
├── requirements.txt                # All dependencies
├── .env                            # API keys (never commit this)
├── .env.example                    # Template for .env
├── .gitignore
│
├── agent/
│   ├── __init__.py
│   ├── core.py                     # LangChain agent router
│   ├── prompts.py                  # All system prompts
│   └── memory.py                   # Conversation memory handler
│
├── modules/
│   ├── __init__.py
│   ├── symptom_analyzer.py         # Phase 1 — core symptom analysis
│   ├── urgency_classifier.py       # Phase 2 — urgency scoring
│   └── care_referral.py            # Phase 3 — hospital/facility referral
│
├── rag/
│   ├── __init__.py
│   ├── loader.py                   # PDF/text ingestion into ChromaDB
│   ├── retriever.py                # Query ChromaDB for relevant chunks
│   └── embeddings.py               # Embedding model setup
│
├── data/
│   ├── docs/                       # Place all health PDFs here
│   │   ├── dghs/                   # DGHS guidelines PDFs
│   │   ├── iedcr/                  # IEDCR disease factsheets
│   │   └── who_bd/                 # WHO Bangladesh documents
│   ├── hospitals.json              # Bangladesh hospital directory
│   └── chroma_db/                  # Auto-created by ChromaDB
│
├── utils/
│   ├── __init__.py
│   ├── language.py                 # Bengali/English detection
│   └── disclaimer.py               # Disclaimer text constants
│
└── tests/
    ├── test_symptom_analyzer.py
    ├── test_urgency_classifier.py
    └── test_rag.py
```

---

## Phase 1 — Core Symptom Chat (Weeks 1–2)

### Goal
A working Streamlit chat app where users describe symptoms and get a safe, informative, BD-context-aware response. No RAG yet — LLM only with a strong system prompt.

### Step 1.1 — Environment setup

Create `.env.example`:
```
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama3-8b-8192
APP_TITLE=BD Health Assistant
```

Create `.env` (fill in real keys, never commit):
```
GROQ_API_KEY=<get free key from console.groq.com>
LLM_PROVIDER=groq
LLM_MODEL=llama3-8b-8192
APP_TITLE=BD Health Assistant
```

Create `.gitignore`:
```
.env
__pycache__/
*.pyc
data/chroma_db/
*.egg-info/
.DS_Store
```

### Step 1.2 — requirements.txt

```txt
streamlit==1.35.0
langchain==0.2.0
langchain-groq==0.1.6
langchain-community==0.2.0
langchain-core==0.2.0
python-dotenv==1.0.1
chromadb==0.5.0
llama-index==0.10.43
llama-index-vector-stores-chroma==0.1.9
sentence-transformers==3.0.1
langdetect==1.0.9
```

Install with:
```bash
pip install -r requirements.txt
```

### Step 1.3 — config.py

```python
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
```

### Step 1.4 — utils/disclaimer.py

```python
DISCLAIMER_EN = (
    "\n\n---\n"
    "⚠️ **Important:** This is general health information only, not medical advice. "
    "Please consult a registered MBBS doctor or visit your nearest health facility "
    "for proper diagnosis and treatment."
)

DISCLAIMER_BN = (
    "\n\n---\n"
    "⚠️ **গুরুত্বপূর্ণ:** এটি শুধুমাত্র সাধারণ স্বাস্থ্য তথ্য, চিকিৎসা পরামর্শ নয়। "
    "সঠিক রোগ নির্ণয় ও চিকিৎসার জন্য অনুগ্রহ করে নিকটস্থ নিবন্ধিত ডাক্তার বা "
    "স্বাস্থ্য কেন্দ্রে যোগাযোগ করুন।"
)

EMERGENCY_MESSAGE_EN = (
    "🚨 **EMERGENCY:** Your symptoms suggest a potentially serious condition. "
    "Call **999** immediately or go to the nearest hospital emergency department. "
    "Do not wait."
)

EMERGENCY_MESSAGE_BN = (
    "🚨 **জরুরি অবস্থা:** আপনার উপসর্গ গুরুতর হতে পারে। "
    "এখনই **999** কল করুন বা নিকটস্থ হাসপাতালের জরুরি বিভাগে যান।"
)
```

### Step 1.5 — utils/language.py

```python
from langdetect import detect

def detect_language(text: str) -> str:
    """Returns 'bn' for Bengali, 'en' for English, defaults to 'en'."""
    try:
        lang = detect(text)
        return lang if lang in ["bn", "en"] else "en"
    except Exception:
        return "en"

def is_bengali(text: str) -> bool:
    return detect_language(text) == "bn"
```

### Step 1.6 — agent/prompts.py

```python
SYSTEM_PROMPT = """
You are a helpful, responsible healthcare information assistant designed specifically 
for the population of Bangladesh. Your role is to:

1. Listen carefully to the user's described symptoms
2. Provide educational information about possible conditions that match those symptoms,
   with specific relevance to diseases common in Bangladesh
3. Never diagnose or prescribe medicine
4. Always recommend professional medical consultation
5. Be sensitive to the healthcare context of Bangladesh — reference government health 
   facilities, upazila health complexes, DGHS guidelines where appropriate
6. Respond in the same language the user writes in (Bengali or English)
7. Keep responses clear, simple, and accessible to people with basic literacy

DISEASES COMMON IN BANGLADESH TO CONSIDER:
Dengue fever, typhoid, chikungunya, diarrheal diseases, cholera, tuberculosis (TB),
malaria (especially Chittagong Hill Tracts), acute respiratory infections, diabetes,
hypertension, skin infections (fungal), eye infections, intestinal worm infestation,
viral hepatitis (jaundice), nutritional anemia, arsenicosis (in some regions).

RESPONSE FORMAT — always follow this structure:
1. Acknowledge the symptoms with empathy
2. Mention 2-3 possible conditions these symptoms may relate to (educational, not diagnostic)
3. Provide brief, simple information about each condition
4. State urgency level: Low / Medium / High / Emergency
5. Recommend appropriate action (home care tips, when to see a doctor, which facility)
6. End with the medical disclaimer

IMPORTANT RULES:
- Never say "you have [disease]" — always say "your symptoms may be related to..."
- Never recommend specific medicines, brands, or dosages
- Always end with disclaimer
- For emergency symptoms (chest pain, difficulty breathing, unconsciousness, 
  severe bleeding, signs of stroke), immediately tell user to call 999
- Be compassionate — many users may be anxious about their health
"""

SYMPTOM_ANALYSIS_TEMPLATE = """
Based on the following symptoms described by a patient in Bangladesh, provide a 
careful, responsible health information response following the format in your 
system instructions.

Patient symptoms: {symptoms}

Additional context from health documents:
{context}

Respond in {language}.
"""

URGENCY_CLASSIFICATION_PROMPT = """
Given these symptoms: {symptoms}

Classify the urgency level as exactly one of: low, medium, high, emergency

Use these Bangladesh-specific guidelines:
- emergency: chest pain, difficulty breathing, loss of consciousness, severe bleeding,
  signs of stroke (face drooping, arm weakness, speech difficulty), snake bite, 
  severe burn, high fever with convulsions in children
- high: high fever (>39°C / 102°F) for more than 2 days, severe dehydration, 
  blood in stool or urine, severe abdominal pain, suspected dengue with warning signs
- medium: fever for 1-2 days, moderate diarrhea, persistent cough, skin rash,
  eye discharge, mild to moderate pain
- low: mild cold, minor skin irritation, mild headache, minor digestive issues

Respond with ONLY one word: low, medium, high, or emergency
"""
```

### Step 1.7 — agent/memory.py

```python
from langchain.memory import ConversationBufferWindowMemory

def get_memory(k: int = 5) -> ConversationBufferWindowMemory:
    """
    Returns a sliding window conversation memory.
    k=5 means it remembers the last 5 exchanges.
    """
    return ConversationBufferWindowMemory(
        k=k,
        memory_key="chat_history",
        return_messages=True,
        output_key="output"
    )
```

### Step 1.8 — agent/core.py

```python
from langchain_groq import ChatGroq
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from config import GROQ_API_KEY, LLM_MODEL
from agent.prompts import SYSTEM_PROMPT
from agent.memory import get_memory
from utils.disclaimer import DISCLAIMER_EN, DISCLAIMER_BN, EMERGENCY_MESSAGE_EN
from utils.language import detect_language

def get_llm():
    """Initialize and return the LLM."""
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=0.3,      # lower temperature = more consistent, safer responses
        max_tokens=1024,
    )

def get_agent_response(user_input: str, chat_history: list, context: str = "") -> str:
    """
    Main agent function. Takes user symptom input, optional RAG context,
    and returns a safe, formatted health information response.
    """
    llm = get_llm()
    lang = detect_language(user_input)

    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(content=SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])

    # Inject RAG context into input if available
    enriched_input = user_input
    if context:
        enriched_input = (
            f"{user_input}\n\n[Relevant health information from Bangladesh "
            f"health documents:\n{context}]"
        )

    chain = prompt | llm
    response = chain.invoke({
        "chat_history": chat_history,
        "input": enriched_input
    })

    response_text = response.content

    # Append appropriate disclaimer
    disclaimer = DISCLAIMER_BN if lang == "bn" else DISCLAIMER_EN
    return response_text + disclaimer
```

### Step 1.9 — modules/symptom_analyzer.py

```python
from agent.core import get_agent_response
from agent.prompts import URGENCY_CLASSIFICATION_PROMPT
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL
from utils.disclaimer import EMERGENCY_MESSAGE_EN, EMERGENCY_MESSAGE_BN
from utils.language import detect_language

def classify_urgency(symptoms: str) -> str:
    """Returns urgency level: low / medium / high / emergency"""
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model_name=LLM_MODEL,
        temperature=0,
        max_tokens=10
    )
    prompt = URGENCY_CLASSIFICATION_PROMPT.format(symptoms=symptoms)
    result = llm.invoke(prompt)
    urgency = result.content.strip().lower()
    valid = ["low", "medium", "high", "emergency"]
    return urgency if urgency in valid else "medium"

def analyze_symptoms(symptoms: str, chat_history: list, context: str = "") -> dict:
    """
    Main symptom analysis function.
    Returns dict with response text, urgency level, and language.
    """
    lang = detect_language(symptoms)
    urgency = classify_urgency(symptoms)

    # For emergency, prepend urgent message before regular response
    prefix = ""
    if urgency == "emergency":
        prefix = (EMERGENCY_MESSAGE_BN if lang == "bn" else EMERGENCY_MESSAGE_EN) + "\n\n"

    response = get_agent_response(symptoms, chat_history, context)

    return {
        "response": prefix + response,
        "urgency": urgency,
        "language": lang
    }
```

### Step 1.10 — app.py (Phase 1 — no RAG yet)

```python
import streamlit as st
from config import APP_TITLE, APP_ICON
from modules.symptom_analyzer import analyze_symptoms

# Page config
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="centered"
)

# Urgency color map
URGENCY_COLORS = {
    "low": "🟢",
    "medium": "🟡",
    "high": "🟠",
    "emergency": "🔴"
}

# Header
st.title(f"{APP_ICON} {APP_TITLE}")
st.caption("Describe your symptoms and get health information relevant to Bangladesh. "
           "Available in English and বাংলা.")

st.info(
    "ℹ️ This assistant provides general health information only. "
    "It is not a substitute for professional medical advice.",
    icon="ℹ️"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("urgency"):
            urgency = msg["urgency"]
            icon = URGENCY_COLORS.get(urgency, "⚪")
            st.caption(f"Urgency level: {icon} {urgency.upper()}")

# Chat input
if prompt := st.chat_input("Describe your symptoms... / আপনার উপসর্গ বলুন..."):

    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Analyzing symptoms..."):
            result = analyze_symptoms(
                symptoms=prompt,
                chat_history=st.session_state.chat_history
            )

        st.markdown(result["response"])
        urgency = result["urgency"]
        icon = URGENCY_COLORS.get(urgency, "⚪")
        st.caption(f"Urgency level: {icon} {urgency.upper()}")

    # Save to session
    st.session_state.messages.append({
        "role": "assistant",
        "content": result["response"],
        "urgency": urgency
    })

    # Update LangChain chat history (last 5 exchanges)
    from langchain_core.messages import HumanMessage, AIMessage
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    st.session_state.chat_history.append(AIMessage(content=result["response"]))
    if len(st.session_state.chat_history) > 10:
        st.session_state.chat_history = st.session_state.chat_history[-10:]

# Sidebar
with st.sidebar:
    st.header("About")
    st.write(
        "This tool provides health information based on symptoms. "
        "It covers common diseases in Bangladesh including dengue, typhoid, "
        "tuberculosis, diarrheal diseases, and more."
    )
    st.divider()
    st.subheader("Emergency Contacts 🇧🇩")
    st.write("🚨 National Emergency: **999**")
    st.write("🏥 DGHS Hotline: **16401**")
    st.write("🦠 IEDCR Hotline: **10655**")
    st.divider()
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.rerun()
```

### Phase 1 — Run and verify

```bash
streamlit run app.py
```

Expected behavior: Chat UI opens, user can type symptoms, agent responds with health info, urgency badge appears, disclaimer is always shown. Verify with these test inputs:
- "I have fever and headache for 2 days"
- "আমার জ্বর এবং শরীর ব্যথা"
- "I have chest pain and difficulty breathing" (should trigger emergency)

---

## Phase 2 — RAG over Bangladesh Health Documents (Weeks 3–4)

### Goal
Load real health documents from DGHS, IEDCR, and WHO Bangladesh into ChromaDB. Agent responses are now grounded in actual Bangladesh health guidelines.

### Step 2.1 — Download free source documents

Download these free public PDFs and place them in `data/docs/`:

| Source | URL | Place in folder |
|--------|-----|-----------------|
| IEDCR disease factsheets | iedcr.gov.bd | data/docs/iedcr/ |
| DGHS health bulletins | dghs.gov.bd | data/docs/dghs/ |
| WHO Bangladesh fact sheets | who.int/bangladesh | data/docs/who_bd/ |
| NIPSOM reports | nipsom.gov.bd | data/docs/dghs/ |

As a fallback if PDFs are unavailable, create a file `data/docs/manual_knowledge.txt` and fill it with structured health information about BD diseases (the agent will ingest this too).

### Step 2.2 — rag/embeddings.py

```python
from langchain_community.embeddings import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL

def get_embeddings():
    """
    Returns multilingual sentence-transformer embeddings.
    Supports both Bengali and English — critical for this project.
    Model: paraphrase-multilingual-MiniLM-L12-v2 (free, runs locally)
    """
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True}
    )
```

### Step 2.3 — rag/loader.py

```python
import os
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    DirectoryLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
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
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    vector_store.persist()
    print(f"Vector store built and saved to {CHROMA_DB_PATH}")
    return vector_store

# Run this script directly to build the index
if __name__ == "__main__":
    build_vector_store(force_rebuild=True)
    print("Done. Vector store is ready.")
```

### Step 2.4 — rag/retriever.py

```python
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
                f"[Source {i} — {source_type}]: {doc.page_content.strip()}"
            )

        return "\n\n".join(context_parts)

    except Exception as e:
        print(f"RAG retrieval error: {e}")
        return ""
```

### Step 2.5 — Update modules/symptom_analyzer.py to use RAG

Replace the `analyze_symptoms` function with this RAG-enabled version:

```python
from rag.retriever import retrieve_context

def analyze_symptoms(symptoms: str, chat_history: list, use_rag: bool = True) -> dict:
    """
    Symptom analysis with optional RAG context injection.
    """
    lang = detect_language(symptoms)
    urgency = classify_urgency(symptoms)

    # Retrieve relevant context from health documents
    context = ""
    if use_rag:
        context = retrieve_context(symptoms)

    prefix = ""
    if urgency == "emergency":
        prefix = (EMERGENCY_MESSAGE_BN if lang == "bn" else EMERGENCY_MESSAGE_EN) + "\n\n"

    response = get_agent_response(symptoms, chat_history, context)

    return {
        "response": prefix + response,
        "urgency": urgency,
        "language": lang,
        "rag_used": bool(context)
    }
```

### Step 2.6 — Build the vector store

```bash
python rag/loader.py
```

This ingests all PDFs in `data/docs/` and builds the ChromaDB index. Run this once. Re-run with `force_rebuild=True` whenever you add new documents.

### Phase 2 — Verify

Add `st.caption(f"📚 RAG context used: {result['rag_used']}")` in `app.py` temporarily to confirm RAG is being used. Remove before final deployment.

---

## Phase 3 — Care Referral Module (Weeks 5–6)

### Goal
When a user asks where to go or the agent determines they need care, it recommends the appropriate Bangladesh healthcare facility based on their urgency level and location.

### Step 3.1 — data/hospitals.json

```json
{
  "emergency_numbers": {
    "national_emergency": "999",
    "dghs_hotline": "16401",
    "iedcr_hotline": "10655",
    "ambulance": "199"
  },
  "facility_tiers": {
    "community_clinic": {
      "description": "Community Clinic — free primary care, nearest to home",
      "when_to_go": "Minor illnesses, routine checkups, family planning, vaccination",
      "cost": "Free",
      "available_in": "All unions"
    },
    "upazila_health_complex": {
      "description": "Upazila Health Complex — free government hospital",
      "when_to_go": "Moderate illness, referral from community clinic, general OPD",
      "cost": "Free (government)",
      "available_in": "All upazilas"
    },
    "district_hospital": {
      "description": "District General Hospital — larger government facility",
      "when_to_go": "Conditions requiring specialist care or minor surgery",
      "cost": "Minimal (government)",
      "available_in": "All district headquarters"
    },
    "medical_college_hospital": {
      "description": "Medical College Hospital — specialized care",
      "when_to_go": "Complex conditions, serious illness, specialist consultation",
      "cost": "Minimal (government) or paid (private)",
      "examples": ["DMCH Dhaka", "Chittagong Medical College", "Rajshahi Medical College",
                   "Sylhet MAG Osmani Medical College", "Khulna Medical College"]
    }
  },
  "major_hospitals_dhaka": [
    {"name": "Dhaka Medical College Hospital (DMCH)", "type": "government", "phone": "02-55165088"},
    {"name": "BSMMU (PG Hospital)", "type": "government", "phone": "02-9661041"},
    {"name": "Sir Salimullah Medical College (Mitford)", "type": "government", "phone": "02-7111321"},
    {"name": "National Institute of Diseases of Chest and Hospital (NIDCH)", "type": "government", "specialty": "TB/Chest"},
    {"name": "National Eye Care", "type": "government", "specialty": "Eye"},
    {"name": "Infectious Disease Hospital (IDH)", "type": "government", "specialty": "Infectious disease"}
  ],
  "urgency_to_facility": {
    "low": "community_clinic",
    "medium": "upazila_health_complex",
    "high": "district_hospital",
    "emergency": "emergency_department"
  }
}
```

### Step 3.2 — modules/care_referral.py

```python
import json
from pathlib import Path
from config import URGENCY_EMERGENCY, URGENCY_HIGH, URGENCY_MEDIUM, URGENCY_LOW

def load_hospital_data() -> dict:
    hospital_path = Path("data/hospitals.json")
    if not hospital_path.exists():
        return {}
    with open(hospital_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_referral(urgency: str, division: str = None) -> dict:
    """
    Returns care referral recommendation based on urgency level.
    Optional division parameter for location-specific recommendations.
    """
    data = load_hospital_data()
    tiers = data.get("facility_tiers", {})
    emergency_numbers = data.get("emergency_numbers", {})
    urgency_map = data.get("urgency_to_facility", {})

    if urgency == URGENCY_EMERGENCY:
        return {
            "action": "EMERGENCY — Call 999 immediately or go to nearest hospital",
            "call": emergency_numbers.get("national_emergency", "999"),
            "facility_type": "Emergency Department",
            "message_en": (
                "This is an emergency. Call **999** immediately or go to the nearest "
                "hospital emergency department. Do not wait."
            ),
            "message_bn": (
                "এটি একটি জরুরি অবস্থা। এখনই **999** কল করুন অথবা নিকটস্থ "
                "হাসপাতালের জরুরি বিভাগে যান। দেরি করবেন না।"
            )
        }

    facility_key = urgency_map.get(urgency, "upazila_health_complex")
    facility = tiers.get(facility_key, {})

    return {
        "action": f"Visit: {facility.get('description', 'nearest health facility')}",
        "when_to_go": facility.get("when_to_go", ""),
        "cost": facility.get("cost", ""),
        "facility_type": facility_key,
        "dghs_hotline": emergency_numbers.get("dghs_hotline", "16401"),
        "message_en": (
            f"Based on your symptoms, we recommend visiting a "
            f"**{facility.get('description', 'health facility')}**. "
            f"{facility.get('when_to_go', '')} Cost: {facility.get('cost', 'varies')}. "
            f"For guidance, call DGHS health line: **16401**."
        )
    }

def format_referral_card(urgency: str) -> str:
    """Returns a formatted markdown referral recommendation."""
    referral = get_referral(urgency)
    if urgency == URGENCY_EMERGENCY:
        return f"🚨 **{referral['action']}**\n\n{referral['message_en']}"
    return (
        f"🏥 **Recommended facility:** {referral['action']}\n\n"
        f"📋 **When to use this facility:** {referral.get('when_to_go', '')}\n\n"
        f"💰 **Cost:** {referral.get('cost', 'varies')}\n\n"
        f"📞 **DGHS health line:** {referral.get('dghs_hotline', '16401')}"
    )
```

### Step 3.3 — Update app.py to show referral card

Add this block inside the chat response section in `app.py`, after displaying the agent response:

```python
from modules.care_referral import format_referral_card

# Show referral card in expander (not intrusive)
with st.expander("🏥 Where to go for care"):
    st.markdown(format_referral_card(urgency))
```

### Phase 3 — Verify

Test with:
- Low urgency symptom → should recommend Community Clinic
- High urgency symptom → should recommend District Hospital
- Emergency symptom → should show 999 prominently

---

## Phase 4 — Hardening and Deployment (Weeks 7–8)

### Step 4.1 — Safety guardrails in agent/core.py

Add input validation before processing. Append this to `agent/core.py`:

```python
BLOCKED_INPUTS = [
    "what medicine should i take",
    "which medicine",
    "prescribe",
    "give me prescription",
    "dosage",
    "how many mg",
    "আমাকে ওষুধ দিন",
    "কোন ওষুধ খাব"
]

def is_medicine_request(text: str) -> bool:
    """Detect if user is asking for medicine prescription."""
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in BLOCKED_INPUTS)

MEDICINE_REFUSAL_EN = (
    "I'm not able to recommend or prescribe specific medicines. "
    "Only a registered doctor can safely prescribe medication after examining you. "
    "Please visit your nearest health facility or call DGHS helpline **16401**."
)

MEDICINE_REFUSAL_BN = (
    "আমি কোনো নির্দিষ্ট ওষুধ সুপারিশ বা প্রেসক্রাইব করতে পারব না। "
    "শুধুমাত্র একজন নিবন্ধিত ডাক্তার আপনাকে পরীক্ষা করার পরে নিরাপদভাবে ওষুধ দিতে পারেন। "
    "অনুগ্রহ করে নিকটস্থ স্বাস্থ্য কেন্দ্রে যান বা DGHS হেল্পলাইন **16401** কল করুন।"
)
```

Update `get_agent_response` to check this before processing:

```python
def get_agent_response(user_input: str, chat_history: list, context: str = "") -> str:
    lang = detect_language(user_input)

    # Safety guardrail — refuse medicine requests
    if is_medicine_request(user_input):
        refusal = MEDICINE_REFUSAL_BN if lang == "bn" else MEDICINE_REFUSAL_EN
        disclaimer = DISCLAIMER_BN if lang == "bn" else DISCLAIMER_EN
        return refusal + disclaimer

    # ... rest of existing function
```

### Step 4.2 — tests/test_symptom_analyzer.py

```python
import pytest
from modules.symptom_analyzer import classify_urgency, analyze_symptoms

def test_emergency_classification():
    result = classify_urgency("chest pain and difficulty breathing")
    assert result == "emergency"

def test_low_urgency():
    result = classify_urgency("mild runny nose and sneezing")
    assert result in ["low", "medium"]

def test_response_contains_disclaimer():
    result = analyze_symptoms("I have fever", [], use_rag=False)
    assert "not medical advice" in result["response"].lower() or \
           "চিকিৎসা পরামর্শ নয়" in result["response"]

def test_bengali_detection():
    result = analyze_symptoms("আমার জ্বর হয়েছে", [], use_rag=False)
    assert result["language"] == "bn"
```

Run tests:
```bash
pytest tests/ -v
```

### Step 4.3 — Deploy to Streamlit Cloud (free)

1. Push project to a GitHub repository (public or private)
2. Go to share.streamlit.io
3. Connect your GitHub repository
4. Set main file path: `app.py`
5. Add secrets in Streamlit Cloud dashboard:
   ```
   GROQ_API_KEY = "your_key_here"
   LLM_PROVIDER = "groq"
   LLM_MODEL = "llama3-8b-8192"
   ```
6. Deploy — free tier gives you 1 app with public URL

**Important for deployment:** ChromaDB must be pre-built. Commit `data/chroma_db/` to the repo OR run `python rag/loader.py` as a startup command in Streamlit Cloud settings.

---

## Data Sources Reference

All free, publicly downloadable:

| Source | URL | Content |
|--------|-----|---------|
| DGHS Bangladesh | dghs.gov.bd | Health guidelines, disease control programs |
| IEDCR | iedcr.gov.bd | Outbreak reports, disease factsheets |
| WHO Bangladesh | who.int/bangladesh | Disease profiles, health statistics |
| NIPSOM | nipsom.gov.bd | Preventive medicine guidelines |
| CDC Traveler's Health | wwwnc.cdc.gov/travel/destinations/traveler/none/bangladesh | Bangladesh-specific disease info |

---

## Tech Stack Summary

| Component | Technology | Cost |
|-----------|-----------|------|
| LLM | Groq API (llama3-8b-8192) | Free tier |
| RAG framework | LlamaIndex + LangChain | Free (open source) |
| Vector database | ChromaDB | Free (local) |
| Embeddings | HuggingFace sentence-transformers | Free (local) |
| UI | Streamlit | Free |
| Hosting | Streamlit Cloud | Free (1 app) |
| PDF parsing | PyPDF | Free (open source) |

**Total cost: ৳0**

---

## Key Rules for the Agent (Summary)

1. Never prescribe medicine — refuse and redirect to doctor
2. Always end every response with the disclaimer
3. For emergency symptoms, show 999 immediately and prominently
4. Never say "you have [disease]" — always say "may be related to"
5. Support both Bengali and English in the same session
6. Ground responses in Bangladesh-specific health context
7. Recommend government health facilities — most users cannot afford private care
8. Keep language simple — literacy levels vary widely across BD population

---

*End of implementation document. Build Phase 1 first, verify it works, then proceed to Phase 2.*
