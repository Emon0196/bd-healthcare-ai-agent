# BD Healthcare Symptom Assistant 🏥

An empathetic, RAG-grounded healthcare symptom assistant designed specifically for the population of Bangladesh. The application runs in both English and Bengali, analyzing user symptoms to classify urgency levels (low, medium, high, emergency), and providing local health facility referrals based on Bangladesh's healthcare infrastructure.

---

## 🌟 Key Features

1. **Bilingual Symptom Analysis:** Supports natural language query inputs in both English and Bengali (বাংলা). It automatically detects the language and responds in the same format.
2. **Interactive UI Modes:**
   - **💬 Conversational Chat:** Talk to an AI health assistant about symptoms and receive educational guidance.
   - **📋 Guided Symptom Checker:** A structured diagnostic wizard enabling users to select symptoms, duration, and regional location to generate a care recommendation report.
3. **Safety & Prescription Refusal Guardrail:** Blocks and refuses medicine recommendations or prescription dosage requests (bilingually) to prevent self-medication, prompting the user to consult an MBBS doctor.
4. **Urgency Classification:** Dynamically rates urgency into four categories (`low`, `medium`, `high`, `emergency`) based on clinical guidelines. If emergency symptoms (e.g., chest pain, shortness of breath, stroke symptoms) are detected, it presents a prominent flashing alert directing the user to dial 999.
5. **RAG Context Grounding:** Integrates a local Vector Database (ChromaDB) containing regional factsheets and WHO/DGHS guidelines to ground responses and avoid AI hallucinations.
6. **Local Care Referral:** Recommends appropriate healthcare facility tiers in Bangladesh (Community Clinics, Upazila Health Complexes, District General Hospitals, or Medical Colleges) along with cost guides and hotlines.

---

## 📂 Project Structure

```
bd_healthcare_agent/
├── app.py                          # Streamlit application entry point (UI)
├── config.py                       # All settings, models, and folder constants
├── requirements.txt                # Python package dependencies
├── README.md                       # Comprehensive project guide (this file)
├── .env                            # Environment secrets (ignored by Git)
├── .env.example                    # Template for environment settings
├── .gitignore                      # Git ignored files & databases
│
├── agent/
│   ├── __init__.py                 # Packaged agent module
│   ├── core.py                     # LangChain agent execution & safety guardrails
│   ├── prompts.py                  # System system instructions & classification prompts
│   └── memory.py                   # Chat history window handler
│
├── modules/
│   ├── __init__.py
│   ├── symptom_analyzer.py         # Main analyzer coordinating RAG + LLM + safety
│   └── care_referral.py            # Local facility referral mapping
│
├── rag/
│   ├── __init__.py
│   ├── embeddings.py               # HuggingFace multilingual embeddings setup
│   ├── loader.py                   # Document splitter & ChromaDB vector store builder
│   └── retriever.py                # Database retrieval similarity search
│
├── data/
│   ├── docs/                       # Grounding knowledge source documents
│   │   └── manual_knowledge.txt    # Multilingual clinical factsheet for target diseases
│   ├── hospitals.json              # Bangladesh hospital metadata & national hotlines
│   └── chroma_db/                  # Local Vector DB files (auto-created)
│
└── tests/
    ├── __init__.py
    └── test_symptom_analyzer.py    # Unit tests verifying core symptom processing
```

---

## 🛠️ Setup & Installation

### Prerequisites
- **Python 3.11 or 3.12** installed on your system.
- A free API key from [Groq Console](https://console.groq.com/).

### Step 1: Clone or Copy the Repository
Navigate to the project root directory.

### Step 2: Initialize Virtual Environment
Create a virtual environment (`venv`) and install dependencies:
```bash
# Create venv
python -m venv venv

# Activate venv (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate venv (Linux/macOS)
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### Step 3: Configure Environment Settings
Create a `.env` file in the root directory (based on `.env.example`):
```ini
GROQ_API_KEY=your_groq_api_key_here
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
APP_TITLE=BD Health Assistant
```

### Step 4: Ingest Documents & Build the RAG Database
Run the ingestion script to parse the manual health guidelines and generate vector embeddings:
```bash
python rag/loader.py
```
This will read data from `data/docs/manual_knowledge.txt` and create a persistent Chroma database under `data/chroma_db/`.

---

## 🚀 Running the App

Start the Streamlit application server:
```bash
streamlit run app.py
```
Open your browser and navigate to **[http://localhost:8501](http://localhost:8501)** to interact with the symptom assistant.

---

## 🧪 Running Automated Tests

Run the unit tests with `pytest` to verify the accuracy of language detection, urgency categorization, and prescription blocks:
```bash
pytest tests/ -v
```

---

## 🛡️ Medical Safety & Disclaimer

This application is strictly educational. It does **not** prescribe medicine or provide official medical diagnoses. Every generated response includes the following mandated disclaimer:

> ⚠️ **Important:** This is general health information only, not medical advice. Please consult a registered MBBS doctor or visit your nearest health facility for proper diagnosis and treatment.

Emergency inputs immediately prompt a warning to call **999** or visit the nearest hospital emergency ward.
