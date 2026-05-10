from app.comparison import build_comparison_reply
from app.intent import REFUSAL_REPLY, Intent, detect_intent
from app.retriever import search_catalog
from app.schemas import ChatRequest, ChatResponse, Recommendation


def _clarification_reply() -> str:
    return (
        "I can help recommend SHL assessments. What role, seniority, key skills, "
        "and assessment type are you hiring for?"
    )


def _empty_recommendation_reply() -> str:
    return (
        "I can help with SHL assessment recommendations. Please share the role, "
        "key skills, and whether you need ability, personality, knowledge, "
        "simulation, or mixed assessments."
    )


def _reply_for_recommendations(intent: Intent, count: int) -> str:
    if intent.action == "finalize":
        return "Confirmed. Here is the final SHL assessment shortlist based on the conversation."

    if intent.action == "refine":
        return f"Updated the shortlist based on your latest constraints. Here are {count} SHL assessments."

    return "Here are SHL assessments that best match the role and requirements you described."


def _validated_recommendations(items: list[dict[str, str]]) -> list[Recommendation]:
    seen_urls = set()
    recommendations = []

    for item in items[:10]:
        name = item.get("name", "").strip()
        url = item.get("url", "").strip()
        test_type = item.get("test_type", "").strip()

        if not name or not url or url in seen_urls:
            continue

        recommendations.append(Recommendation(name=name, url=url, test_type=test_type))
        seen_urls.add(url)

    return recommendations


def handle_chat(request: ChatRequest) -> ChatResponse:
    intent = detect_intent(request)

    if intent.action == "refuse":
        return ChatResponse(
            reply=REFUSAL_REPLY,
            recommendations=[],
            end_of_conversation=False,
        )

    if intent.action == "compare":
        return ChatResponse(
            reply=build_comparison_reply(intent.latest_user_text),
            recommendations=[],
            end_of_conversation=False,
        )

    if intent.action == "clarify":
        return ChatResponse(
            reply=_clarification_reply(),
            recommendations=[],
            end_of_conversation=False,
        )

    recommendations = _validated_recommendations(
        search_catalog(
            intent.user_context,
            limit=10,
            additions=intent.additions,
            removals=intent.removals,
            only=intent.only,
            final_products=intent.final_products,
        )
    )

    if not recommendations:
        return ChatResponse(
            reply=_empty_recommendation_reply(),
            recommendations=[],
            end_of_conversation=False,
        )

    return ChatResponse(
        reply=_reply_for_recommendations(intent, len(recommendations)),
        recommendations=recommendations,
        end_of_conversation=intent.action == "finalize",
    )
