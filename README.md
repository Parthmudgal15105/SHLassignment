# SHL Assessment Recommender

FastAPI service for the SHL AI Intern take-home assignment. It accepts a stateless conversation history and returns the next assistant reply plus a structured shortlist of SHL assessment recommendations.

The service is catalog-grounded: recommendations are selected only from the local SHL product catalog JSON, and every returned URL comes from that catalog.

## API

### Health

```http
GET /health
```

Response:

```json
{"status": "ok"}
```

### Chat

```http
POST /chat
```

Request:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "Hiring a senior full stack engineer with Core Java, Spring, SQL, AWS and Docker"
    }
  ]
}
```

Response:

```json
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
```

The response schema is fixed and validated with Pydantic.

## Behavior

- Clarifies vague requests before recommending.
- Recommends 1 to 10 SHL assessments once enough context is available.
- Uses the full stateless conversation history for refinements.
- Supports additions/removals such as "add personality", "remove AWS", "drop REST", and "only cognitive".
- Compares catalog products using aliases such as OPQ, GSA, DSI, and Verify G+.
- Refuses legal/compliance advice, general hiring advice, non-SHL requests, and prompt-injection attempts.
- Falls back to deterministic intent handling when no LLM key is configured.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/download_catalog.py
python -m pytest
```

Run locally:

```bash
uvicorn app.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

## Optional LLM Intent Extraction

The app can use an LLM only to classify the latest user turn and extract constraints. It never accepts LLM-generated product recommendations.

Environment variables:

```text
LLM_PROVIDER=groq
LLM_API_KEY=your_key
LLM_MODEL=llama-3.1-8b-instant
LLM_TIMEOUT_SECONDS=6
```

Supported providers:

- `groq`
- `gemini`

If these variables are missing or the provider times out, the deterministic fallback handles the request.

## Render Deployment

Use the included `render.yaml`, or create a Render Web Service with:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Before submitting, verify:

```bash
curl https://YOUR-RENDER-URL/health
curl -X POST https://YOUR-RENDER-URL/chat ^
  -H "Content-Type: application/json" ^
  -d "{\"messages\":[{\"role\":\"user\",\"content\":\"Hiring graduate financial analysts needing numerical reasoning and finance knowledge\"}]}"
```

## Tests

```bash
python -m pytest
```

Current coverage includes:

- health endpoint
- public trace behavior C1 to C10
- vague-query clarification
- recommendation/refinement behavior
- product comparison and aliases
- legal/general hiring refusal
- prompt-injection refusal
- catalog URL/schema validation

Run the lightweight replay probes:

```bash
python scripts/replay_public_traces.py
```

## Project Structure

```text
app/
  agent.py       # response pipeline
  catalog.py     # catalog loading and normalization
  comparison.py  # product alias resolution and comparison replies
  intent.py      # LLM/fallback intent extraction
  llm.py         # optional Groq/Gemini calls
  main.py        # FastAPI routes
  retriever.py   # catalog ranking and refinement filters
  schemas.py     # request/response schemas
data/
  raw_catalog.json
  shl_catalog.json
scripts/
  download_catalog.py
  inspect_catalog.py
  replay_public_traces.py
tests/
  test_api.py
  test_public_traces.py
```
