# SHL Assessment Recommender

A FastAPI-based conversational recommender system for selecting SHL assessments from the official SHL product catalog.

This project was built for the SHL AI Intern take-home assignment. The system accepts a stateless conversation history and returns the next assistant reply along with a structured shortlist of SHL assessment recommendations.

---

## Problem Statement

Recruiters and hiring managers often describe hiring needs conversationally instead of knowing the exact assessment names they need. This project helps convert a user’s hiring context into a shortlist of relevant SHL assessments.

The recommender supports:

- Clarifying vague requests
- Recommending 1–10 SHL assessments
- Refining recommendations when the user changes constraints
- Comparing SHL assessments
- Refusing legal, general hiring, non-SHL, and prompt-injection requests
- Returning only catalog-grounded SHL products and URLs

---

## API Endpoints

### Health Check

```http
GET /health

Response:

{
  "status": "ok"
}
Chat Endpoint
POST /chat

Request:

{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a senior full stack engineer with Core Java, Spring, SQL, AWS and Docker"
    }
  ]
}

Response:

{
  "reply": "Here are SHL assessments that best match the role and requirements you described.",
  "recommendations": [
    {
      "name": "Core Java (Advanced Level) (New)",
      "url": "https://www.shl.com/products/product-catalog/view/core-java-advanced-level-new/",
      "test_type": "Knowledge & Skills"
    }
  ],
  "end_of_conversation": false
}

The response schema is fixed and validated using Pydantic.

Tech Stack
Python
FastAPI
Uvicorn
Pydantic
Requests
Pytest
SHL product catalog JSON
Project Structure
SHLassignment/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── catalog.py
│   ├── retriever.py
│   └── comparison.py
│
├── data/
│   ├── raw_catalog.json
│   └── shl_catalog.json
│
├── scripts/
│   ├── download_catalog.py
│   └── inspect_catalog.py
│
├── tests/
│   ├── test_api.py
│   └── test_public_traces.py
│
├── requirements.txt
├── pytest.ini
└── README.md
Catalog Source

The recommender uses the SHL product catalog:

https://tcp-us-prod-rnd.shl.com/voiceRater/shl-ai-hiring/shl_product_catalog.json

The original catalog had invalid control characters, so the download script uses:

json.loads(raw_text, strict=False)

This creates a cleaned local catalog file:

data/shl_catalog.json

The raw downloaded version is also stored as:

data/raw_catalog.json
Setup Instructions
1. Clone or open the project
cd SHLassignment
2. Install dependencies
pip install -r requirements.txt
3. Download the SHL catalog
python scripts/download_catalog.py
4. Inspect the catalog
python scripts/inspect_catalog.py
5. Run the FastAPI server
uvicorn app.main:app --reload

Open Swagger UI:

http://127.0.0.1:8000/docs
Testing

Run all tests:

python -m pytest

Current test status:

17 passed

Test coverage includes:

/health
vague query clarification
senior Java/backend engineer recommendation
OPQ comparison
legal refusal
C1–C10 public trace behavior
OPQ removal refinement
final conversation handling
Example Queries
Vague Query

Input:

{
  "messages": [
    {
      "role": "user",
      "content": "I need an assessment"
    }
  ]
}

Expected behavior:

No recommendations
Ask a clarification question
Senior Backend Engineer

Input:

{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a senior full stack engineer with Core Java, Spring, SQL, AWS and Docker"
    }
  ]
}

Expected recommendations include:

Core Java (Advanced Level) (New)
Spring (New)
SQL (New)
Amazon Web Services (AWS) Development (New)
Docker (New)
SHL Verify Interactive G+
Occupational Personality Questionnaire OPQ32r
Comparison Query

Input:

{
  "messages": [
    {
      "role": "user",
      "content": "What is the difference between OPQ and OPQ MQ Sales Report?"
    }
  ]
}

Expected behavior:

Compare products using catalog-grounded information
Return no recommendations
Keep end_of_conversation as false
Legal Refusal

Input:

{
  "messages": [
    {
      "role": "user",
      "content": "Are we legally required under HIPAA to test all staff who touch patient records?"
    }
  ]
}

Expected behavior:

Refuse legal/compliance advice
Return no recommendations
Design Approach

The system uses a deterministic, catalog-grounded approach.

Flow
POST /chat
   ↓
Extract latest user message
   ↓
Extract full user conversation history
   ↓
Check off-scope/legal/prompt-injection requests
   ↓
Check comparison requests
   ↓
Check vague queries
   ↓
Retrieve and rank SHL catalog products
   ↓
Apply refinement filters
   ↓
Return schema-safe response
Retrieval Strategy

The current retriever uses:

Preferred product mappings for high-confidence scenarios
Keyword-based scoring over catalog text
Noise filtering for irrelevant products
Explicit exclusion handling for user refinements
Catalog URL validation through local product data

Examples of supported refinements:

Drop REST
Remove OPQ
Add simulation
Final list: Verify G+ and Graduate Scenarios
Guardrails

The system refuses:

Legal advice
Compliance interpretation
General hiring advice outside SHL assessments
Non-SHL recommendations
Prompt-injection attempts

Example refusal:

{
  "reply": "I can only help with SHL assessment recommendations and comparisons from the SHL catalog. I cannot provide legal, compliance, or non-SHL advice.",
  "recommendations": [],
  "end_of_conversation": false
}
Public Trace Coverage

The system was tested against the 10 public traces:

Trace	Scenario	Status
C1	Senior leadership	Passed
C2	Senior Rust networking engineer	Passed
C3	Contact center agents	Passed
C4	Graduate financial analysts	Passed
C5	Sales re-skilling audit	Passed
C6	Chemical plant safety	Passed
C7	Healthcare admin / HIPAA	Passed
C8	Admin Excel/Word	Passed
C9	Senior full-stack engineer	Passed
C10	Graduate management trainee	Passed