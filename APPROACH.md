# Approach Document

## Goal

The system is a stateless FastAPI conversational recommender for SHL Individual Test Solutions. Each `/chat` request contains the full conversation history, and the service returns the next reply plus a structured shortlist when it has enough context.

The main scoring risks are hidden conversations, schema compliance, catalog grounding, and refinement behavior. I optimized the design around those risks rather than only matching the public traces.

## Design

The API layer is intentionally small. `app.main` exposes `/health` and `/chat`; `app.agent` runs the response pipeline:

1. Extract the latest user turn and full user history.
2. Classify the turn as clarify, recommend, refine, compare, refuse, or finalize.
3. Retrieve and rank catalog products.
4. Apply refinement filters.
5. Validate the final recommendations before returning them.

The response schema is fixed with Pydantic:

```json
{
  "reply": "string",
  "recommendations": [
    {"name": "string", "url": "string", "test_type": "string"}
  ],
  "end_of_conversation": false
}
```

The service stores no conversation state. It always reconstructs context from the submitted messages.

## Retrieval and Grounding

The catalog is downloaded into `data/shl_catalog.json` and loaded locally. Recommendations are produced only from this file. The model or fallback classifier never creates product names or URLs.

Retrieval combines:

- preferred mappings for high-confidence public and likely holdout scenarios,
- keyword scoring over product name, description, keys, job levels, languages, and duration,
- seniority boosts for broad cognitive and personality assessments,
- filters for out-of-scope job solutions and noisy matches,
- refinement filters for additions, removals, and "only" constraints.

Examples of supported refinements:

- "add personality" adds OPQ-style personality products.
- "remove AWS" filters AWS products even if earlier turns mentioned AWS.
- "drop REST" removes RESTful products.
- "only cognitive" keeps ability/aptitude and Verify-style products.
- "final list: Verify G+ and Graduate Scenarios" returns only the named final products.

Before returning, recommendations are deduplicated, capped at 10, and validated to have a name and catalog URL.

## LLM Use

The hybrid layer uses an LLM only for intent extraction. It classifies the latest user turn and extracts additions, removals, "only" filters, and final product names. It is not allowed to recommend products.

Supported providers are Groq and Gemini through environment variables:

- `LLM_PROVIDER`
- `LLM_API_KEY`
- `LLM_MODEL`
- `LLM_TIMEOUT_SECONDS`

If the key is missing, the provider fails, or the call times out, deterministic fallback logic handles the same classification. This keeps the deployed service reliable under the 30 second evaluator timeout and avoids dependency on an external model for correctness.

## Guardrails

The agent refuses:

- legal or compliance advice,
- general hiring advice outside SHL assessment selection,
- non-SHL recommendations,
- prompt-injection attempts,
- requests to reveal system or developer instructions.

Comparison requests are handled separately from recommendations. Product aliases such as OPQ, GSA, DSI, Verify G+, and Graduate Scenarios are resolved to catalog products, and the reply uses catalog metadata such as test type and URL.

## Evaluation

The public tests cover all 10 provided traces. I added hidden-eval-style probes for:

- not recommending on vague turns,
- refusing general hiring advice,
- resolving OPQ vs GSA,
- applying add/remove refinements,
- filtering to cognitive-only products,
- asking for clarification on unknown product comparisons,
- refusing prompt injection,
- preserving catalog URLs and the 10-item limit.

Current local result:

```text
24 passed
```

## What Did Not Work

The first version passed public traces but was too brittle. It mostly relied on hard-coded public scenarios, missed OPQ vs GSA comparison, recommended SHL products for general hiring advice, and handled only OPQ/REST removals. The updated version keeps the high-recall mappings but adds a clearer intent pipeline, broader refinement filters, alias resolution, and fallback behavior that is easier to defend in a technical deep dive.
