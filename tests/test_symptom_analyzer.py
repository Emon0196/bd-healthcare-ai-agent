import pytest
from modules.symptom_analyzer import classify_urgency, analyze_symptoms
from agent.core import is_medicine_request, MEDICINE_REFUSAL_EN, MEDICINE_REFUSAL_BN

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

def test_medicine_request_check():
    assert is_medicine_request("what medicine should i take?") is True
    assert is_medicine_request("কোন ওষুধ খাব") is True
    assert is_medicine_request("I have fever and headache") is False

def test_medicine_refusal_response():
    result = analyze_symptoms("prescribe some paracetamol please", [], use_rag=False)
    assert "not able to recommend or prescribe" in result["response"].lower()
    
    result_bn = analyze_symptoms("আমাকে প্যারাসিটামল ওষুধ দিন", [], use_rag=False)
    assert "প্রেসক্রাইব করতে পারব না" in result_bn["response"]
