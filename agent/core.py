from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage

from config import GROQ_API_KEY, LLM_MODEL
from agent.prompts import SYSTEM_PROMPT
from utils.disclaimer import DISCLAIMER_EN, DISCLAIMER_BN
from utils.language import detect_language

BLOCKED_INPUTS = [
    "what medicine should i take",
    "which medicine",
    "prescribe",
    "give me prescription",
    "dosage",
    "how many mg",
    "আমাকে ওষুধ দিন",
    "কোন ওষুধ খাব",
    "medicine recommendation",
    "paracetamol",
    "antibiotic",
    "napa",
    "fexo",
    "tablet",
    "syrup",
    "ওষুধ",
    "ঔষধ",
    "প্যারাসিটামল",
    "মেডিসিন"
]

def is_medicine_request(text: str) -> bool:
    """Detect if user is asking for medicine prescription or recommendation."""
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
    lang = detect_language(user_input)
    disclaimer = DISCLAIMER_BN if lang == "bn" else DISCLAIMER_EN

    # Safety guardrail — refuse medicine requests
    if is_medicine_request(user_input):
        refusal = MEDICINE_REFUSAL_BN if lang == "bn" else MEDICINE_REFUSAL_EN
        return refusal + disclaimer

    llm = get_llm()

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

    return response_text + disclaimer
