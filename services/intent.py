import re


_GREETING_PATTERNS = [
    r"^hi$",
    r"^hello$",
    r"^hey$",
    r"^hii$",
    r"^hola$",
    r"^namaste$",
    r"^नमस्ते$",
    r"^hello वहां$",
    r"good morning",
    r"good evening",
    r"good night",
]

_NOTE_PATTERNS = [
    r"\bnotes?\b",
    r"\bshort notes?\b",
    r"\bsummary\b",
    r"\bimportant points\b",
    r"\bpoints?\b",
    r"नोट्स?",
    r"सारांश",
    r"संक्षेप",
]

_MCQ_PATTERNS = [
    r"\bmcq\b",
    r"\bquiz\b",
    r"\bobjective\b",
    r"\btest\b",
    r"बहुविकल्पीय",
    r"प्रश्नोत्तरी",
]

_EXPLAIN_PATTERNS = [
    r"\bexplain\b",
    r"\bexplains?\b",
    r"\bexplanation\b",
    r"\bhow\b",
    r"\bwhy\b",
    r"\bwhat is\b",
    r"समझाओ",
    r"समझाइए",
    r"बताओ",
    r"क्यों",
    r"कैसे",
    r"अर्थ",
    r"व्याख्या",
    r"नियम",
    r"सिद्धांत",
    r"सूत्र",
    r"law",
    r"theory",
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return True
    return False


def is_greeting(text: str) -> bool:
    cleaned = (text or "").strip().lower()
    return _matches_any(cleaned, _GREETING_PATTERNS)


def detect_intent(text: str) -> str:
    cleaned = (text or "").strip().lower()

    if not cleaned:
        return "chat"

    if _matches_any(cleaned, _NOTE_PATTERNS):
        return "notes"

    if _matches_any(cleaned, _MCQ_PATTERNS):
        return "mcq"

    if _matches_any(cleaned, _EXPLAIN_PATTERNS):
        return "explain"

    if "?" in cleaned:
        return "explain"

    words = cleaned.split()
    if len(words) >= 2 and any(word in cleaned for word in ["newton", "physics", "chemistry", "math", "biology"]):
        return "explain"

    return "chat"
