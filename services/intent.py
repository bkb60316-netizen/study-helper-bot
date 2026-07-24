import re


_GREETING_PATTERNS = [
    r"^hi$",
    r"^hello$",
    r"^hey$",
    r"^hii$",
    r"^namaste$",
    r"^नमस्ते$",
    r"good morning",
    r"good evening",
    r"good night",
]

_NOTE_PATTERNS = [
    r"\bnotes?\b",
    r"\bshort notes?\b",
    r"\bsummary\b",
    r"\bimportant points\b",
    r"\bkey points\b",
    r"\brevision\b",
    r"\brevise\b",
    r"\bmake notes\b",
    r"\bwrite notes\b",
    r"\bnotes on\b",
    r"नोट्स?",
    r"सारांश",
    r"संक्षेप",
    r"पॉइंट्स?",
]

_MCQ_PATTERNS = [
    r"\bmcq\b",
    r"\bmcqs\b",
    r"\bobjective\b",
    r"\bquiz\b",
    r"\btest\b",
    r"\bmultiple choice\b",
    r"बहुविकल्पीय",
    r"प्रश्नोत्तरी",
]

_EXPLAIN_PATTERNS = [
    r"\bexplain\b",
    r"\bexplanation\b",
    r"\bwhat is\b",
    r"\bwhy\b",
    r"\bhow\b",
    r"\bsolve\b",
    r"\bderive\b",
    r"\bderivation\b",
    r"\blaw\b",
    r"\btheory\b",
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
]


def _matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


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

    return "chat"
