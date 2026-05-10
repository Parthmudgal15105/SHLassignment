# Changes Since Handoff

This file summarizes the changes made after you handed over the existing SHL assignment project, plus the remaining steps to prepare the final submission.

## What Was Added

### Hybrid Agent Pipeline

- Added `app/agent.py` as the main `/chat` orchestration layer.
- Added `app/intent.py` to classify each user turn as:
  - clarify
  - recommend
  - refine
  - compare
  - refuse
  - finalize
- Added `app/llm.py` for optional LLM-based intent extraction through environment variables.
- Kept a deterministic fallback so the app still works when no LLM key is configured or the LLM times out.

### API Contract Preserved

- Kept `GET /health` unchanged.
- Kept `POST /chat` response schema unchanged:
  - `reply`
  - `recommendations`
  - `end_of_conversation`
- Simplified `app/main.py` so FastAPI routes call the new agent pipeline.

### Stronger Retrieval and Refinement

- Improved `app/retriever.py` so recommendations remain catalog-grounded.
- Added support for broader refinement behavior:
  - "add personality"
  - "remove AWS"
  - "drop REST"
  - "only cognitive"
  - final shortlist requests
- Added filtering to avoid returning removed products when earlier conversation turns mentioned them.
- Kept recommendations capped at 10 items.
- Preserved catalog-only product names and URLs.

### Better Comparison Support

- Improved `app/comparison.py` alias handling.
- Added support for aliases such as:
  - `OPQ`
  - `GSA`
  - `DSI`
  - `Verify G+`
  - `Graduate Scenarios`
- Fixed the earlier failure where `OPQ vs GSA` did not resolve both products.

### Stronger Guardrails

- Added refusal behavior for:
  - legal questions
  - compliance advice
  - general hiring advice outside SHL assessment selection
  - non-SHL recommendations
  - prompt-injection attempts
  - requests to reveal system/developer instructions

### Testing Improvements

- Expanded `tests/test_api.py` with hidden-eval-style probes.
- Added coverage for:
  - vague query clarification
  - general hiring refusal
  - `OPQ` vs `GSA` comparison
  - add/remove refinements
  - cognitive-only filtering
  - unknown product comparison
  - prompt-injection refusal
  - recommendation URL and count validation
- Current test result after changes:

```text
24 passed
```

### Submission Readiness

- Rewrote `README.md` with cleaner setup, API, testing, LLM, and deployment instructions.
- Added `APPROACH.md` as the concise approach document for the submission.
- Added `render.yaml` for Render deployment.
- Added `scripts/replay_public_traces.py` for lightweight smoke testing.
- Added `.gitignore` to prevent committing Python cache files, virtual environments, and local env files.

## Files Changed or Added

Important new files:

- `app/agent.py`
- `app/intent.py`
- `app/llm.py`
- `APPROACH.md`
- `CHANGES.md`
- `render.yaml`
- `.gitignore`
- `scripts/replay_public_traces.py`

Important modified files:

- `app/main.py`
- `app/retriever.py`
- `app/comparison.py`
- `tests/test_api.py`
- `README.md`

## Further Steps

1. Review the approach document.
   - Open `APPROACH.md`.
   - Trim wording if the submission form has a strict two-page upload requirement.

2. Run final local checks.

```bash
python -m pytest
python scripts/replay_public_traces.py
```

3. Remove tracked cache files from Git if needed.

```bash
git rm -r --cached app/__pycache__ tests/__pycache__
```

4. Commit the final project.

```bash
git add .
git commit -m "Improve SHL recommender robustness"
```

5. Push to GitHub.

```bash
git push origin main
```

6. Deploy on Render.
   - Connect the GitHub repository to Render.
   - Use `render.yaml` if Render detects it.
   - Otherwise configure manually:

```bash
Build command: pip install -r requirements.txt
Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

7. Configure optional LLM environment variables on Render.

```text
LLM_PROVIDER=groq
LLM_API_KEY=your_key_here
LLM_MODEL=llama-3.1-8b-instant
LLM_TIMEOUT_SECONDS=6
```

The app works without these variables because deterministic fallback is built in.

8. Verify the public Render URL.

```bash
curl https://YOUR-RENDER-URL/health
```

Then test `/chat` with a sample request.

9. Submit the assignment form with:
   - public Render API URL
   - approach document
   - GitHub repository link if requested

## Final Notes

- The project is now stronger for hidden evaluator behavior than the original public-trace-only version.
- The most important remaining task is public deployment and endpoint verification.
- Be ready to explain in interviews that the LLM is used only for intent extraction, while all product recommendations are validated against the SHL catalog.
