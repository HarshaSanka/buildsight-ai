# Verification record

Verified on 7 November 2026. This records observed checks and their scope, not production readiness.

## Local application

- Fresh Python 3.13 environment installed the exact `requirements.lock` successfully.
- `pip check`: no broken requirements.
- `ruff check .`: passed.
- `pytest -q`: **14 passed**.
- `python scripts/evaluate.py`: **5/5 fixture queries retrieved their expected document in the top 3**; all returned citation quotes matched their source.
- `python scripts/smoke.py` against a real local Uvicorn server: passed health, citations, pending schedule review, high-risk finding, rejection and simulated Procore checks.
- Browser demonstration: observed cited results, pending review, rejection, final card-based approval display and reviewer/reason/UTC timestamp.
- Markdown local links checked; architecture diagrams supplied as editable Mermaid and SVG.

## Automated behavior coverage

The 14 cases cover authentication/input validation, citation integrity and no-match abstention, six combinations of specialist workflow and approval/rejection, restart recovery, graph and mock endpoints, risk/date rules, optional-model valid output, invalid-quote fallback and timeout fallback. Multiple assertions within each case exercise related failure conditions, including missing runs and duplicate terminal decisions.

## Container and GitHub verification

The repository is published at [HarshaSanka/buildsight-ai](https://github.com/HarshaSanka/buildsight-ai).

[Initial GitHub verification run](https://github.com/HarshaSanka/buildsight-ai/actions/runs/42423045303) completed successfully on Linux with Python 3.13. It installed dependencies, passed lint/tests/evaluation, built the Docker image, started the non-root application container and passed its health probe. Later revisions also run `scripts/smoke.py` against the container; inspect the [latest Actions results](https://github.com/HarshaSanka/buildsight-ai/actions) for the current commit.

Docker is not installed on the development machine; observed image build and container runtime evidence came from GitHub Actions, not local Docker execution. Compose configuration is supplied but was not executed locally. No registry image publication or cloud deployment is claimed.

## Limits

The retrieval set is tiny, synthetic and hand-authored using fixture vocabulary. Its perfect Recall@3 is a regression result and cannot support a real-world accuracy claim. Exact quote integrity is not proof of relevance, source validity or generated-claim entailment.

The optional Ollama adapter was tested with simulated transport/model responses, not a live installed model. No real Procore/Autodesk API, OAuth flow, BIM geometry, production identity system, trained predictive model, cloud deployment, multi-process coordination, load test or construction field validation was performed. Human decisions affect local advisory state only.
