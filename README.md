LLM Router
==========

LLMRouter is a toy vet-clinic customer-support stack that routes user questions to the correct agent (FAQ vs. order) and can benchmark different LLMs for the classifier.

Requirements
------------

- Python 3.10+
- API keys saved in a `.env` file at the repo root:
  - `OPENAI_API_KEY`
  - `GOOGLE_API_KEY` (if you plan to exercise Gemini beyond free limits)
  - `ANTHROPIC_API_KEY`
  - `GROQ_API_KEY`

Setup
-----

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # or pip install -e . if you package it
```

The entrypoints rely on package-relative imports, so run them as modules:

- Interactive demo:

  ```bash
  python -m src.main
  ```

- Model evaluation:

  ```bash
  python -m src.evaluation
  ```

Both commands assume `.venv` is active and `.env` is loaded; `src/router/call_LLM.py` uses `python-dotenv` to load `.env` automatically.

Notes
-----

- `src/router/call_LLM.py` currently defaults to `call_openai`. Switch to `call_gemini` in `src/main.py` if you want to test Gemini and retrieve the complete response.
- If the LLM call fails (`Error calling …`), the router falls back to a simple keyword heuristic (see `src/router/router.py`) to make sure the router provides suitable answers (instead of errors or None) by running `main.py`. For accurate evaluations make sure API keys are valid and outbound network access is available.
- `src/evaluation.py` is the individual evaluation and testing file and will generate a file similar to `detailed_results.txt` and display similar outputs to `detailed_results.txt`

Evaluation Criteria
-------------------

`python -m src.evaluation` runs 20 intent-classification prompts against each configured LLM and reports:

- **Accuracy** – percent of test cases with the correct routing decision.
- **Latency** – average, p50, and p95 times (ms) per classification call.
- **Error log** – any misclassifications with the offending query/response.

Results (latest run)
--------------------

| Model             | Accuracy | Avg Latency | P95 Latency |
|-------------------|----------|-------------|-------------|
| GPT-4o-mini       | 100%     | 516 ms      | 962 ms      |
| Gemini 2.0 Flash  | 100%     | 613 ms      | 858 ms      |
| Claude Sonnet 4   | 100%     | 2482 ms     | 3583 ms     |
| Llama 3 70B 8k    | 85%      | 2229 ms     | 5380 ms     |

See `all_results.txt` / `detailed_results.txt` for the raw run logs.

Conclusion
----------

- GPT-4o-mini currently provides the best overall balance: perfect accuracy with the lowest average latency among the top performers.
- Gemini 2.0 Flash ties for accuracy but is slightly slower;
- Claude Sonnet 4 remains accurate yet much more latent;
-  Llama 3 70B trails in both accuracy and speed on this workload, so it is not recommended without additional tuning.

We could further enhance accuracy by implementing a two-stage approach where the LLM:
**Verification Pipeline:**
1. Initial intent classification: Query → LLM → Intent₁
2. Verification pass: (Query, Intent₁) → LLM → Confidence score
3. If confidence < threshold, reclassify or fallback

However, this approach would **double the token consumption** and increase latency by ~2x, making it impractical for real-time customer service applications where response speed is critical.