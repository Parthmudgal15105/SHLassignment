from fastapi import FastAPI

from app.comparison import is_comparison_query, build_comparison_reply
from app.retriever import search_catalog
from app.schemas import ChatRequest, ChatResponse, Recommendation

app = FastAPI(title="SHL Assessment Recommender")


@app.get("/health")
def health():
    return {"status": "ok"}


def get_latest_user_message(request: ChatRequest) -> str:
    for message in reversed(request.messages):
        if message.role == "user":
            return message.content
    return ""


def get_user_conversation_text(request: ChatRequest) -> str:
    user_messages = []

    for message in request.messages:
        if message.role == "user":
            user_messages.append(message.content)

    return "\n".join(user_messages)


def is_vague_query(text: str) -> bool:
    text = text.lower().strip()

    vague_phrases = [
        "i need an assessment",
        "need an assessment",
        "recommend assessment",
        "recommend an assessment",
        "need a test",
        "help me choose",
    ]

    if text in vague_phrases:
        return True

    if len(text.split()) <= 4 and "assessment" in text:
        return True

    return False


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

    return any(phrase in text for phrase in confirmation_phrases)


def is_out_of_scope(text: str) -> bool:
    text = text.lower()

    blocked_phrases = [
        "legal",
        "legally",
        "law",
        "compliance requirement",
        "required under",
        "satisfy that requirement",
        "ignore previous instructions",
        "ignore above",
        "system prompt",
        "developer message",
        "non-shl",
        "non shl",
        "recommend non",
    ]

    return any(phrase in text for phrase in blocked_phrases)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    latest_user_text = get_latest_user_message(request)
    full_user_context = get_user_conversation_text(request)

    # 1. Refuse off-scope queries
    if is_out_of_scope(latest_user_text):
        return ChatResponse(
            reply=(
                "I can only help with SHL assessment recommendations and comparisons "
                "from the SHL catalog. I cannot provide legal, compliance, or non-SHL advice."
            ),
            recommendations=[],
            end_of_conversation=False,
        )

    # 2. Handle comparison questions
    if is_comparison_query(latest_user_text):
        return ChatResponse(
            reply=build_comparison_reply(latest_user_text),
            recommendations=[],
            end_of_conversation=False,
        )

    # 3. Clarify vague queries
    if is_vague_query(latest_user_text):
        return ChatResponse(
            reply="I can help recommend SHL assessments. What role, skills, and assessment type are you hiring for?",
            recommendations=[],
            end_of_conversation=False,
        )

    # 4. Recommend using full conversation history
    recommendations = search_catalog(full_user_context, limit=10)

    if not recommendations:
        return ChatResponse(
            reply=(
                "I can help with SHL assessment recommendations. Please share the role, "
                "key skills, and whether you need ability, personality, knowledge, simulation, or mixed assessments."
            ),
            recommendations=[],
            end_of_conversation=False,
        )

    end_conversation = is_confirmation(latest_user_text)

    if end_conversation:
        reply = "Confirmed. Here is the final SHL assessment shortlist based on the conversation."
    else:
        reply = "Here are SHL assessments that best match the role and requirements you described."

    return ChatResponse(
        reply=reply,
        recommendations=[Recommendation(**item) for item in recommendations],
        end_of_conversation=end_conversation,
    )