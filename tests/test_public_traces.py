from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def post_chat(messages):
    response = client.post("/chat", json={"messages": messages})
    assert response.status_code == 200
    return response.json()


def names(data):
    return [item["name"] for item in data["recommendations"]]


def assert_contains_all(actual_names, expected_names):
    for expected in expected_names:
        assert expected in actual_names


def test_c1_senior_leadership():
    data = post_chat(
        [
            {
                "role": "user",
                "content": "We need a solution for senior leadership.",
            },
            {
                "role": "assistant",
                "content": "Who is this meant for?",
            },
            {
                "role": "user",
                "content": (
                    "The pool consists of CXOs, director-level positions; people with more than "
                    "15 years of experience. Selection — comparing candidates against a leadership benchmark."
                ),
            },
        ]
    )

    assert_contains_all(
        names(data),
        [
            "Occupational Personality Questionnaire OPQ32r",
            "OPQ Universal Competency Report 2.0",
            "OPQ Leadership Report",
        ],
    )
    assert data["end_of_conversation"] is False


def test_c2_rust_networking_engineer():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "I'm hiring a senior Rust engineer for high-performance networking "
                    "infrastructure. What assessments should I use?"
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "Smart Interview Live Coding",
            "Linux Programming (General)",
            "Networking and Implementation (New)",
            "SHL Verify Interactive G+",
            "Occupational Personality Questionnaire OPQ32r",
        ],
    )


def test_c3_contact_center_english_us():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "We're screening 500 entry-level contact centre agents. "
                    "Inbound calls, customer service focus. English US."
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "SVAR - Spoken English (US) (New)",
            "Contact Center Call Simulation (New)",
            "Entry Level Customer Serv-Retail & Contact Center",
            "Customer Service Phone Simulation",
        ],
    )


def test_c4_graduate_financial_analysts():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "Hiring graduate financial analysts — final-year students, no work experience. "
                    "We need numerical reasoning, a finance knowledge test, and situational judgement."
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "SHL Verify Interactive – Numerical Reasoning",
            "Financial Accounting (New)",
            "Basic Statistics (New)",
            "Graduate Scenarios",
            "Occupational Personality Questionnaire OPQ32r",
        ],
    )


def test_c5_sales_reskilling_audit():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "As part of our restructuring and annual talent audit, we need to "
                    "re-skill our Sales organization. What solutions do you recommend?"
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "Global Skills Assessment",
            "Global Skills Development Report",
            "Occupational Personality Questionnaire OPQ32r",
            "OPQ MQ Sales Report",
            "Sales Transformation 2.0 - Individual Contributor",
        ],
    )


def test_c6_chemical_plant_safety():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "We're hiring plant operators for a chemical facility. Safety is absolute "
                    "top priority — reliability, procedure compliance, never cutting corners. "
                    "What do you recommend?"
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "Dependability and Safety Instrument (DSI)",
            "Manufac. & Indust. - Safety & Dependability 8.0",
            "Workplace Health and Safety (New)",
        ],
    )


def test_c7_healthcare_admin_hybrid():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "We're hiring bilingual healthcare admin staff in South Texas. They handle "
                    "patient records and need to be assessed in Spanish. HIPAA compliance is critical. "
                    "They are functionally bilingual and English fluent for written work. Go with the hybrid."
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "HIPAA (Security)",
            "Medical Terminology (New)",
            "Microsoft Word 365 - Essentials (New)",
            "Dependability and Safety Instrument (DSI)",
            "Occupational Personality Questionnaire OPQ32r",
        ],
    )


def test_c8_admin_excel_word_simulation():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "I need to quickly screen admin assistants for Excel and Word daily. "
                    "I am OK with adding a simulation - we want to capture the capabilities."
                ),
            }
        ]
    )

    actual = names(data)

    assert_contains_all(
        actual,
        [
            "Microsoft Excel 365 (New)",
            "Microsoft Word 365 (New)",
            "MS Excel (New)",
            "MS Word (New)",
            "Occupational Personality Questionnaire OPQ32r",
        ],
    )


def test_c9_senior_full_stack_engineer_refinement():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "Here's the JD for an engineer we need to fill. Senior Full-Stack Engineer "
                    "with Core Java, Spring, REST API design, Angular, SQL, AWS deployment, and Docker."
                ),
            },
            {
                "role": "assistant",
                "content": "Is this backend-leaning or frontend-heavy?",
            },
            {
                "role": "user",
                "content": (
                    "Backend-leaning. Day-one priorities are Core Java and Spring; SQL is constant."
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

    actual = names(data)

    assert_contains_all(
        actual,
        [
            "Core Java (Advanced Level) (New)",
            "Spring (New)",
            "SQL (New)",
            "Amazon Web Services (AWS) Development (New)",
            "Docker (New)",
            "SHL Verify Interactive G+",
            "Occupational Personality Questionnaire OPQ32r",
        ],
    )

    assert "RESTful Web Services (New)" not in actual


def test_c10_graduate_management_trainee_initial():
    data = post_chat(
        [
            {
                "role": "user",
                "content": (
                    "We run a graduate management trainee scheme. We need a full battery — "
                    "cognitive, personality, and situational judgement. All recent graduates."
                ),
            }
        ]
    )

    assert_contains_all(
        names(data),
        [
            "SHL Verify Interactive G+",
            "Occupational Personality Questionnaire OPQ32r",
            "Graduate Scenarios",
        ],
    )


def test_c10_graduate_management_trainee_final_without_opq():
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

    assert names(data) == [
        "SHL Verify Interactive G+",
        "Graduate Scenarios",
    ]
    assert data["end_of_conversation"] is True
