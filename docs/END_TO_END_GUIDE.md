# BuildSight AI — End-to-End Project Guide

## 1. Purpose and business context

Construction project information is scattered across RFIs, specifications, submittals, daily reports, schedules and model metadata. A project engineer investigating a blocked concrete pour needs both textual evidence and relationships: which RFI blocks which activity, which later activities depend on it, and who must review a proposed action.

BuildSight demonstrates a small but complete local software slice of that problem. Its primary user is a project engineer preparing an advisory review for field leadership. A superintendent may inspect the evidence; a reviewer records a disposition. These are demonstration personas, not separately authenticated enterprise roles.

The project is independent of Kokosing. It uses no actual construction project records and claims no measured operational savings. Its value as a portfolio project is that the entire path from fictional input through retrieval, orchestration, review and recovery can be inspected and executed.

## 2. Vocabulary

| Term | Meaning in this project |
|---|---|
| RFI | Request for information; RFI-014 asks about a reinforcing conflict |
| Submittal | Material/design information submitted for review; SUB-008 records an approved mix |
| Float | Time an activity can slip without affecting its modeled completion constraint; fixture value only |
| Lookahead | Near-term schedule view, represented by seven-day risk rules |
| BIM | Building information modeling; represented here only by a synthetic element identifier |
| Citation | Document ID, section and exact stored quote supporting a retrieved answer |
| Checkpoint | Saved LangGraph state used to recover a paused workflow |
| Human in the loop | A workflow waits for an authenticated reviewer before its local disposition changes |

## 3. Requirements and acceptance behavior

A successful local installation must answer an evidence question with verifiable citations, identify the open RFI blocker, trace downstream activities, route all three specialist workflows, pause before disposition, accept approval or rejection, prevent another decision, and recover a pending review after process restart. It must make no external vendor write. Tests encode these behaviors rather than claiming field efficacy.

The application must run with synthetic fixtures and no paid services. It must disclose its extractive retrieval and deterministic rules. A small browser demonstration and API documentation make it reviewable by both technical and construction stakeholders.

## 4. Inputs and data contracts

`data/project.json` is the single input snapshot. It contains project metadata, six documents, four activities, one RFI and one element. The project date is fixed at 2026-11-07. Identifiers are deliberately stable so a user can compare UI output, test expectations and source records.

Documents preserve `id`, `title`, `section` and `text`. The index combines title and text for ranking, but citations always quote the original text. Activities contain planned dates, float, status and predecessor IDs. RFIs hold status, due date, affected activity and element. The fixture's graph links are explicit relationships, not model-discovered assertions.

The two mock connector endpoints read the same snapshot. They simulate integration boundaries and normalized records, not the actual response schemas of Procore or Autodesk. Vendor documentation and authorized sandbox accounts would be required before implementing real adapters.

## 5. Installation and first run

Follow the root README to create a Python 3.13 environment, install the locked dependencies and start Uvicorn. Run from the repository root. The default checkpoint path is `state/buildsight.sqlite`; `BUILDSIGHT_DB` can select another location. The application creates the parent directory when needed. The process needs write permission there.

Open the browser demo. Keep the service bound to localhost. Enter your configured API key. The default key is suitable only for a local synthetic demonstration. The health endpoint and page are public; data endpoints require the shared key.

The startup lifespan opens SQLite, enables WAL, builds the knowledge index and graph, and compiles the LangGraph workflow with its SQLite saver. The corpus index and NetworkX graph rebuild on every startup; workflow state remains in SQLite.

## 6. Scenario A: explain a potential deck pour delay

Ask: **Which unresolved RFIs could delay the bridge deck pour?** The search ranks document title/text vectors by cosine similarity. Returned evidence may include RFI-014, the concrete specification and the lookahead schedule. Inspect document IDs and exact quotations rather than relying on a fluent summary.

RFI-014 says the reinforcing conflicts with embedded drainage at pier P2 and blocks ACT-030. The concrete specification requires conflicts to be resolved before placement. The schedule says ACT-030 has zero float. These are separate evidence records; a quoted specification is not evidence that an engineer has actually resolved the field condition.

Now choose the schedule workflow and create a review. The graph traverses from ACT-030 to curing and barrier installation. The result reports a high heuristic severity because the activity starts within seven days and has zero float. It does not calculate an actual three-day delay or a completion-date shift.

## 7. Scenario B: human review

The run is returned as `awaiting_approval`. Its state holds the query, specialist kind, analysis date, evidence, findings and draft. No approval decision exists yet. Read the draft, compare evidence with the fixture and write a reason.

Reject with a reason such as “Engineer disposition remains pending.” The workflow resumes through LangGraph `Command(resume=...)`, records the shared local reviewer identity and ends in `rejected`. A second decision returns HTTP 409. Approval records `approved` but also ends without an external side effect. Source fixture status remains open.

This separation is intentional: approving an advisory record is different from approving an engineering design, responding to a contractual RFI or authorizing construction. A production adapter would need a separately designed action/outbox stage and carefully scoped permissions.

## 8. Scenario C: persistence and recovery

Create a review and save its returned ID. Stop Uvicorn gracefully. Restart it with the same database path. GET `/runs/{id}` should still report `awaiting_approval`. Submit a decision and observe the terminal state. `test_restart` automates the same process using two application lifespans and a temporary disk database.

The local lock serializes workflow mutation and snapshots within one server process. Run one Uvicorn worker. Multiple independent replicas are outside this design. A deployed system needs a distributed coordination mechanism, production checkpoint storage and appropriate request idempotency.

## 9. Scenario D: abstention and unsupported requests

Ask about “quantum cryptocurrency.” With no lexical evidence, the service returns insufficient evidence, no citations and `abstained: true`. This is a no-match mechanism, not a comprehensive factuality classifier. A query sharing generic construction terms can still retrieve irrelevant passages. Exact quotation integrity proves source copying, not relevance or correctness.

The default mode does not execute instructions found in documents or call a language model. Optional Ollama synthesis treats passages as untrusted input and checks citations, but requires human claim review. Document text is rendered using `textContent` in the browser. When enabling generation, keep tool permissions outside model control and test adversarial documents. Quote matching does not prove claim entailment.

## 10. Code walkthrough

`Knowledge.__init__` reads JSON, fits a TF-IDF vectorizer with English stop words and one/two-word features, and builds a directed graph. `search` transforms a query with the fitted vocabulary and returns up to three records above the fixed 0.05 cosine threshold. `answer` assembles exact text and citation metadata. `risks` examines open RFIs and calculates date-based severity.

`build_graph` defines a typed state, retrieval node, analysis node, conditional specialist routing, one shared approval node and an end state. The RFI specialist incorporates evidence; schedule and risk specialists describe the findings. Each draft is a deterministic template. “Agent” describes workflow roles here; none is an LLM reasoning agent.

`create_app` initializes resource lifetime, protects endpoints with a shared-key dependency, bounds request lengths and validates workflow types. Requests are synchronous; FastAPI runs them in its threadpool. SQLite access and graph mutation are serialized by a process lock. The app is deliberately small enough to understand without several infrastructure services.

## 11. Testing and evaluation

Run lint, pytest and the retrieval script from the root README. Tests cover missing credentials, invalid input, citations, no-match abstention, approval and rejection across three workflows, duplicate decisions, missing run IDs, graph relationships, simulated integrations, date rules, closed-RFI exclusion and recovery after restart.

The evaluation script uses five hand-authored query/expected-document pairs and checks whether each expected document appears in the top three. It also validates exact source quotes. This set is both tiny and closely related to the fixture wording; it is a regression check, not an independent benchmark. A realistic benchmark would include ambiguous questions, synonyms, drawing references, scanned pages, hard negatives, stale revisions, conflicting sources and expert relevance labels.

## 12. Packaging and delivery

The Docker image installs the locked environment, copies only application/data content and starts the server as a non-root user. Compose mounts a persistent state volume and exposes localhost. GitHub Actions checks code, tests retrieval, builds an image and probes its health. Deployment to a cloud host and image registry publication are future work, not represented as completed deployment.

## 13. Practical extension sequence

1. Add validated ingestion and document revision/provenance handling.
2. Introduce an independently labeled construction evaluation set.
3. Compare TF-IDF against BM25 and semantic embeddings with project/revision filters.
4. Enable and evaluate the optional local generator only after measuring retrieval; source-ID/quote checks are implemented, but claim support needs review.
5. Add authenticated reviewer identities, role checks and immutable audit events.
6. Implement authorized vendor sandbox adapters with rate limits and idempotent writes.
7. Move checkpoint storage and request coordination to a production design.
8. Pilot with qualified construction reviewers before accepting operational use.

Each extension needs its own acceptance criteria. Adding a model or database alone does not make the project production-ready.
