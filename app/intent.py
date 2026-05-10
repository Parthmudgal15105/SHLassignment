from dataclasses import dataclass, field
import re
from typing import Any

from app.llm import extract_intent_with_llm
from app.schemas import ChatRequest


REFUSAL_REPLY = (
    "I can only help with SHL assessment recommendations and comparisons "
    "from the SHL catalog. I cannot provide legal, compliance, general hiring, "
    "prompt-injection, or non-SHL advice."
)


@dataclass
class Intent:
    action: str
    latest_user_text: str
    user_context: str
    additions: list[str] = field(default_factory=list)
    removals: list[str] = field(default_factory=list)
    only: list[str] = field(default_factory=list)
    final_products: list[str] = field(default_factory=list)


def latest_user_message(request: ChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == "user":
            return message.content
    return ""


def user_context(request: ChatRequest) -> str:
    return "\n".join(message.content for message in request.messages if message.role == "user")


def _contains_any(text: str, phrases: list[str]) -> bool:
    return any(phrase in text for phrase in phrases)


def is_confirmation(text: str) -> bool:
    text = text.lower().strip()
    confirmation_phrases = [
        "thanks",
        "thank you",
        "that works",
        "looks good",
        "perfect",
        "confirmed",
        "lock it in",
        "locking it in",
        "that's good",
        "that covers it",
        "go ahead",
        "final list",
        "final shortlist",
        "final battery",
        "final",
        "proceed",
        "we'll use",
    ]
    return _contains_any(text, confirmation_phrases)


def is_comparison_query(text: str) -> bool:
    text = text.lower()
    comparison_terms = [
        "difference between",
        "compare",
        "different from",
        " vs ",
        " versus ",
        "what's the difference",
        "what is the difference",
    ]
    return _contains_any(text, comparison_terms)


def is_refusal_query(text: str) -> bool:
    text = text.lower()

    if _contains_any(
        text,
        [
            "ignore previous instructions",
            "ignore above",
            "system prompt",
            "developer message",
            "reveal your prompt",
            "show your prompt",
            "jailbreak",
            "non-shl",
            "non shl",
            "recommend non",
            "outside shl",
        ],
    ):
        return True

    if _contains_any(
        text,
        [
            "legal",
            "legally",
            "law",
            "compliance requirement",
            "required under",
            "satisfy that requirement",
            "hipaa requires",
        ],
    ):
        return True

    hiring_advice_terms = [
        "interview",
        "culture fit",
        "salary",
        "compensation",
        "job offer",
        "background check",
        "reference check",
        "write a job description",
        "screen resumes",
        "screen cvs",
    ]
    assessment_terms = ["assessment", "test", "shl", "catalog", "recommend", "shortlist"]

    return _contains_any(text, hiring_advice_terms) and not _contains_any(text, assessment_terms)


def is_vague_query(text: str) -> bool:
    text_lower = text.lower().strip()
    tokens = re.findall(r"[a-z0-9+#.]+", text_lower)

    vague_phrases = [
        "i need an assessment",
        "need an assessment",
        "recommend assessment",
        "recommend an assessment",
        "need a test",
        "help me choose",
    ]

    if text_lower in vague_phrases:
        return True

    if len(tokens) <= 4 and ("assessment" in text_lower or "test" in text_lower):
        return True

    if (
        len(tokens) <= 6
        and _contains_any(text_lower, ["hiring", "hire", "recruiting"])
        and not _contains_any(
            text_lower,
            [
                "senior",
                "lead",
                "graduate",
                "entry",
                "sql",
                "spring",
                "aws",
                "docker",
                "excel",
                "word",
                "safety",
                "finance",
                "sales",
                "contact",
                "networking",
                "rust",
            ],
        )
    ):
        return True

    return False


def _extract_terms(text: str, verbs: list[str]) -> list[str]:
    text_lower = text.lower()
    terms = []
    known_terms = [
        "aws",
        "amazon web services",
        "docker",
        "rest",
        "restful",
        "opq",
        "personality",
        "simulation",
        "technical",
        "knowledge",
        "skills",
        "cognitive",
        "ability",
        "aptitude",
        "excel",
        "word",
    ]

    for verb in verbs:
        for term in known_terms:
            if f"{verb} {term}" in text_lower or f"{verb} the {term}" in text_lower:
                terms.append(term)

    if "without opq" in text_lower or "no opq" in text_lower:
        terms.append("opq")
    if "without rest" in text_lower or "no rest" in text_lower:
        terms.append("rest")

    return list(dict.fromkeys(terms))


def _extract_only_terms(text: str) -> list[str]:
    text_lower = text.lower()
    terms = []

    for term in ["cognitive", "ability", "aptitude", "personality", "simulation", "technical"]:
        if f"only {term}" in text_lower or f"just {term}" in text_lower:
            terms.append(term)

    return terms


def _extract_final_products(text: str) -> list[str]:
    text_lower = text.lower()

    if "final list" not in text_lower and "final shortlist" not in text_lower:
        return []

    candidates = []
    aliases = {
        "verify g+": "SHL Verify Interactive G+",
        "g+": "SHL Verify Interactive G+",
        "graduate scenarios": "Graduate Scenarios",
        "opq": "Occupational Personality Questionnaire OPQ32r",
        "global skills assessment": "Global Skills Assessment",
        "gsa": "Global Skills Assessment",
    }

    for alias, name in aliases.items():
        if alias in text_lower and name not in candidates:
            candidates.append(name)

    return candidates


def _prompt_for_llm(request: ChatRequest) -> str:
    lines = []

    for message in request.messages:
        lines.append(f"{message.role}: {message.content}")

    return (
        "Classify the latest user turn. Valid action values are "
        "clarify, recommend, refine, compare, refuse, finalize. Extract additions, "
        "removals, only filters, and final_products as arrays of short strings.\n"
        "Return JSON with keys: action, additions, removals, only, final_products.\n\n"
        + "\n".join(lines)
    )


def _merge_llm(intent: Intent, data: dict[str, Any] | None) -> Intent:
    if not data:
        return intent

    action = data.get("action")
    valid_actions = {"clarify", "recommend", "refine", "compare", "refuse", "finalize"}

    if isinstance(action, str) and action in valid_actions:
        intent.action = action

    for field_name in ["additions", "removals", "only", "final_products"]:
        value = data.get(field_name)
        if isinstance(value, list):
            clean = [str(item).strip() for item in value if str(item).strip()]
            current = getattr(intent, field_name)
            setattr(intent, field_name, list(dict.fromkeys(current + clean)))

    return intent


def detect_intent(request: ChatRequest) -> Intent:
    latest = latest_user_message(request)
    context = user_context(request)
    latest_lower = latest.lower()

    if is_refusal_query(latest):
        action = "refuse"
    elif is_comparison_query(latest):
        action = "compare"
    elif is_vague_query(latest):
        action = "clarify"
    elif is_confirmation(latest):
        action = "finalize"
    elif _contains_any(latest_lower, ["add ", "drop ", "remove ", "without ", "only ", "just "]):
        action = "refine"
    else:
        action = "recommend"

    intent = Intent(
        action=action,
        latest_user_text=latest,
        user_context=context,
        additions=_extract_terms(latest, ["add", "include"]),
        removals=_extract_terms(latest, ["drop", "remove", "skip", "exclude", "without", "no"]),
        only=_extract_only_terms(latest),
        final_products=_extract_final_products(latest),
    )

    llm_data = extract_intent_with_llm(_prompt_for_llm(request))
    return _merge_llm(intent, llm_data)
