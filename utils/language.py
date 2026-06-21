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
