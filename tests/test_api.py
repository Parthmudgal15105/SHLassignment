from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def post_chat(messages):
    response = client.post("/chat", json={"messages": messages})
    assert response.status_code == 200
    return response.json()


def recommendation_names(data):
    return [item["name"] for item in data["recommendations"]]


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_vague_query_clarifies():
    data = post_chat(
        [
            {
                "role": "user",
                "content": "I need an assessment",
            }
        ]
    )

    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False
    assert "what role" in data["reply"].lower()


def test_senior_java_backend_trace():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "Here's the JD for an engineer we need to fill. "
                    "Senior Full-Stack Engineer with Core Java, Spring, "
                    "REST API design, Angular, SQL, AWS deployment, and Docker."
                ),
            },
            {
                "role": "assistant",
                "content": "Is this backend-leaning or frontend-heavy?",
            },
            {
                "role": "user",
                "content": (
                    "Backend-leaning. Day-one priorities are Core Java and Spring; "
                    "SQL is constant."
                ),
            },
            {
                "role": "assistant",
                "content": "Is this senior IC or tech lead?",
            },
            {
                "role": "user",
                "content": "Senior IC. Add AWS and Docker. Drop REST.",
            },
        ]
    )

    names = recommendation_names(data)

    expected = [
        "Core Java (Advanced Level) (New)",
        "Spring (New)",
        "SQL (New)",
        "Amazon Web Services (AWS) Development (New)",
        "Docker (New)",
        "SHL Verify Interactive G+",
        "Occupational Personality Questionnaire OPQ32r",
    ]

    for item in expected:
        assert item in names

    assert "RESTful Web Services (New)" not in names
    assert data["end_of_conversation"] is False


def test_opq_comparison_returns_no_recommendations():
    data = post_chat(
        [
            {
                "role": "user",
                "content": "What is the difference between OPQ and OPQ MQ Sales Report?",
            }
        ]
    )

    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False
    assert "OPQ32r" in data["reply"]
    assert "OPQ MQ Sales Report" in data["reply"]


def test_legal_refusal():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "Are we legally required under HIPAA to test all staff "
                    "who touch patient records?"
                ),
            }
        ]
    )

    assert data["recommendations"] == []
    assert data["end_of_conversation"] is False
    assert "cannot provide legal" in data["reply"].lower()


def test_c10_final_list_removes_opq():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "We run a graduate management trainee scheme. We need a full battery — "
                    "cognitive, personality, and situational judgement. All recent graduates."
                ),
            },
            {
                "role": "assistant",
                "content": "Here are SHL assessments that best match the role and requirements you described.",
            },
            {
                "role": "user",
                "content": "Drop the OPQ. Final list: Verify G+ and Graduate Scenarios.",
            },
        ]
    )

    names = recommendation_names(data)

    assert names == [
        "SHL Verify Interactive G+",
        "Graduate Scenarios",
    ]

    assert data["end_of_conversation"] is True
