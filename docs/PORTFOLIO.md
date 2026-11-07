# Portfolio demonstration and interview guide

## Defensible description

“BuildSight AI is my independent construction intelligence portfolio project. I implemented a FastAPI application with citation-linked lexical retrieval, explicit RFI/schedule relationships, LangGraph specialist workflows and SQLite-backed human approval. It runs on fictional project records and uses simulated vendor interfaces. I also added an optional local Ollama synthesis adapter with source-ID and quotation checks; its automated contract tests use simulated model responses.”

Use this wording only after personally running and understanding the project. Do not imply employment at Kokosing, field deployment, actual Procore/Autodesk experience, proprietary architecture ownership, measured cost savings or a trained predictive model.

## Five-minute demonstration

1. **Problem (30 seconds):** explain the fictional deck pour and scattered evidence.
2. **Evidence (60 seconds):** ask about reinforcing conflict; open the fixture and verify citations.
3. **Relationships (45 seconds):** trace the RFI blocker through curing and barrier activities.
4. **Workflow (90 seconds):** start a schedule review, explain deterministic specialist routing and pending approval, then reject it with a reason.
5. **Engineering (45 seconds):** show restart test, CI and Docker configuration.
6. **Limits (30 seconds):** explain extractive retrieval, simulated integrations and next evaluation steps.

## Suggested project résumé bullets

- Built a synthetic construction intelligence application with FastAPI, citation-linked TF-IDF retrieval and NetworkX relationships connecting RFIs, activities and BIM metadata.
- Implemented LangGraph RFI, schedule and risk review workflows with persisted human approval/rejection and restart recovery using SQLite checkpoints.
- Added automated API/workflow tests, a small retrieval regression harness, Docker packaging and GitHub Actions verification; modeled Procore/Autodesk integration boundaries with clearly labeled mocks.

Do not add adoption, savings, accuracy or scale numbers beyond observed test scope. Five fixture queries are not a real-world accuracy benchmark.

## Questions you should be able to answer

**Why this construction problem?** It connects information retrieval to a concrete coordination workflow and makes the decision boundary visible.

**What is actually agentic?** LangGraph executes typed state transitions and specialist branches, and interrupts for a human decision. The nodes are deterministic functions; there are no autonomous LLM reasoning agents. Optional Ollama synthesis is a bounded retrieval-to-text call, not agent-controlled tool use.

**How do you prevent fabricated citations?** Default responses copy original source text and IDs; the optional generator must return valid IDs and exact quoted spans. That guarantees quote integrity, while relevance and source validity need separate evaluation.

**Is this GraphRAG?** It combines lexical evidence with graph-assisted risk analysis. Graph traversal does not expand or rerank text search, so I describe it precisely rather than claiming a complete GraphRAG pipeline.

**What does approval do?** It records a local advisory review, with reviewer label, reason and timestamp. It never closes a source RFI or authorizes field work.

**How would you integrate Procore?** Start with approved sandbox access and vendor documentation, define typed normalization and OAuth scopes, handle pagination/retries/rate limits, preserve revision provenance and add contract tests. Treat writes as a separately governed action stage.

**How would you measure value?** First gather expert-labeled questions and workflow outcomes; measure retrieval relevance, supported claims, abstention, review time and acceptance. Compare against a baseline using the same scope. Do not infer labor savings from unit tests.

**What would production require?** Identity, authorization before retrieval, secure source ingestion, source revision handling, evaluated models, production checkpoints, coordinated execution, backups, immutable audit, observability and qualified construction governance.
