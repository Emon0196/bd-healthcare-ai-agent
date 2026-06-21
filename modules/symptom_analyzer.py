import os
from agent.core import get_agent_response, is_medicine_request, MEDICINE_REFUSAL_BN, MEDICINE_REFUSAL_EN
from agent.prompts import URGENCY_CLASSIFICATION_PROMPT
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL
from utils.disclaimer import EMERGENCY_MESSAGE_EN, EMERGENCY_MESSAGE_BN, DISCLAIMER_BN, DISCLAIMER_EN
from utils.language import detect_language
from rag.retriever import retrieve_context

def classify_urgency(symptoms: str) -> str:
    """Returns urgency level: low / medium / high / emergency"""
    # Safety Check: Fallback if API key is not configured yet
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        lower_symptoms = symptoms.lower()
        emergency_keywords = ["chest pain", "breathing", "unconscious", "bleeding", "stroke", "convulsion", "snake bite", "তীব্র শ্বাসকষ্ট", "বুকে ব্যথা", "রক্তপাত"]
        high_keywords = ["high fever", "dehydration", "blood in stool", "তীব্র জ্বর", "রক্ত আমাশয়"]
        medium_keywords = ["fever", "cough", "diarrhea", "rash", "জ্বর", "কাশি", "পাতলা পায়খানা"]
        
        if any(k in lower_symptoms for k in emergency_keywords):
            return "emergency"
        if any(k in lower_symptoms for k in high_keywords):
            return "high"
        if any(k in lower_symptoms for k in medium_keywords):
            return "medium"
        return "low"

    try:
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
        # In case LLM returns something with punctuation or extra text
        for v in valid:
            if v in urgency:
                return v
        return "medium"
    except Exception as e:
        print(f"Urgency classification error: {e}")
        # Local keyword-based fallback if API call fails
        lower_symptoms = symptoms.lower()
        if "chest pain" in lower_symptoms or "breathing" in lower_symptoms:
            return "emergency"
        return "medium"

def analyze_symptoms(symptoms: str, chat_history: list, use_rag: bool = True) -> dict:
    """
    Symptom analysis with optional RAG context injection.
    Returns a dict with response, urgency, language, and RAG status.
    """
    lang = detect_language(symptoms)
    disclaimer = DISCLAIMER_BN if lang == "bn" else DISCLAIMER_EN

    # If it is a medicine request, refuse immediately (fast path)
    if is_medicine_request(symptoms):
        refusal = MEDICINE_REFUSAL_BN if lang == "bn" else MEDICINE_REFUSAL_EN
        return {
            "response": refusal + disclaimer,
            "urgency": "low",
            "language": lang,
            "rag_used": False
        }

    # Classify urgency
    urgency = classify_urgency(symptoms)

    # Prepend emergency message for emergency level
    prefix = ""
    if urgency == "emergency":
        prefix = (EMERGENCY_MESSAGE_BN if lang == "bn" else EMERGENCY_MESSAGE_EN) + "\n\n"

    # Retrieve relevant context from ChromaDB
    context = ""
    if use_rag:
        context = retrieve_context(symptoms)

    # Check if API Key is configured before making call
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        missing_key_warning = (
            "⚠️ **API Key Missing:** The Groq API key is not configured in the `.env` file.\n\n"
            "Here is some general information from our database matches regarding your symptoms:\n\n"
        )
        if lang == "bn":
            missing_key_warning = (
                "⚠️ **এপিআই কী অনুপস্থিত:** আপনার `.env` ফাইলে Groq API কী কনফিগার করা নেই।\n\n"
                "আপনার উপসর্গ সম্পর্কিত সাধারণ তথ্য নিচে দেওয়া হলো:\n\n"
            )
        
        # In absence of API key, return the retrieved context itself as a temporary fallback response
        fallback_body = context if context else ("No direct database matches found. Please consult a doctor." if lang == "en" else "কোনো তথ্য খুঁজে পাওয়া যায়নি। অনুগ্রহ করে ডাক্তারের পরামর্শ নিন।")
        return {
            "response": prefix + missing_key_warning + fallback_body + disclaimer,
            "urgency": urgency,
            "language": lang,
            "rag_used": bool(context)
        }

    try:
        response = get_agent_response(symptoms, chat_history, context)
        return {
            "response": prefix + response,
            "urgency": urgency,
            "language": lang,
            "rag_used": bool(context)
        }
    except Exception as e:
        print(f"Agent response generation error: {e}")
        error_msg = "An error occurred while generating response. Please consult a doctor."
        if lang == "bn":
            error_msg = "দুঃখিত, কোনো ত্রুটি ঘটেছে। অনুগ্রহ করে ডাক্তারের পরামর্শ নিন।"
        return {
            "response": prefix + f"⚠️ Error: {str(e)}\n\n{error_msg}" + disclaimer,
            "urgency": urgency,
            "language": lang,
            "rag_used": bool(context)
        }
