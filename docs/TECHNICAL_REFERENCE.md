# Technical reference

## HTTP contract

All JSON endpoints except `/health` require `x-api-key`. `/` serves the public browser demo. The shared key is configured through `BUILDSIGHT_API_KEY`, defaulting to `local-demo-key`. Authentication assigns one demonstration identity, `local-reviewer`.

| Method | Path | Input / output |
|---|---|---|
| GET | `/health` | Process health and synthetic/extractive mode |
| POST | `/ask` | `question` (3–2000 characters); exact excerpts and citations |
| GET | `/graph` | Typed node and edge lists |
| GET | `/integrations/procore` | Fictional RFI records; `simulated: true` |
| GET | `/integrations/autodesk` | Fictional element metadata; `simulated: true` |
| POST | `/runs` | `question`, kind (`rfi`, `schedule`, `risk`), optional ISO `as_of` |
| GET | `/runs/{id}` | Workflow ID, status and state |
| POST | `/runs/{id}/decision` | Boolean `approve` and 3–1000 character `reason` |

Use `/docs` or `/openapi.json` for generated schemas. Invalid keys return 401. Invalid input returns 422. Unknown runs return 404. Repeated terminal decisions return 409. A workflow-creation retry creates a new UUID; generalized idempotency is not implemented.

## Response example

```json
{
  "answer": "Open RFI-014: ... [RFI-014 §description]",
  "citations": [{
    "document_id": "RFI-014",
    "section": "description",
    "quote": "Full original source text is returned here.",
    "score": 0.42
  }],
  "mode": "extractive_tfidf",
  "abstained": false
}
```

This is an abbreviated illustrative schema, not a captured exact response or universal similarity score. Real responses return the full stored text.

## Retrieval mathematics

The vectorizer uses scikit-learn TF-IDF with stop-word removal, unigrams and bigrams, smoothed inverse document frequency and its default L2 normalization. Conceptually `idf(t) = log((1+n)/(1+df(t))) + 1`. Term frequency multiplied by inverse document frequency is normalized to form a document vector. Cosine similarity is the dot product divided by the product of vector norms; for unit vectors it is their dot product.

The query uses the same fitted vocabulary. The corpus is six short section records, so there is no separate chunking service. Ranking sorts by descending score with source order as a deterministic tie break. Top K is three, with a minimum score of 0.05. This threshold was chosen for a readable demonstration and has not been calibrated on field queries. IDs and exact phrases are strong lexical cues; synonyms may fail.

Default citations contain the original ID, section and entire source text. Optional Ollama synthesis returns shorter exact quoted spans after checking their document IDs and membership in retrieved sources. There is no semantic entailment checker: a valid quote can still accompany an unsupported generated claim. Passage relevance, claim support and source validity remain separate concerns.

## Graph representation

Nodes carry stable IDs and a `kind`. Activity edges point from predecessor to successor. An RFI points to its blocked activity and concerned BIM element. The graph is rebuilt from JSON at startup. No edge is inferred by similarity, and the graph does not alter text-search ranking.

Risk traversal begins at the affected activity, using NetworkX descendants. Because the fixture contains only directed schedule edges leaving activities, downstream results are activities. An external ingestion pipeline must validate edge types, reject missing references and cycles in schedule precedence, and distinguish source-provided from inferred relationships.

## Risk algorithm

For every open RFI:

1. Look up its affected activity.
2. Calculate `days_to_start = activity.start - as_of` in calendar days.
3. Mark overdue if RFI due date is earlier than `as_of`.
4. Assign high severity if days-to-start is at most seven and float is zero; otherwise medium.
5. Return direct blocker path and sorted downstream descendants.

A due date equal to the analysis date is not overdue. Past starts can be high severity. Closed RFIs are omitted. There is no “low” tier, numeric probability, cost estimate, activity duration propagation, resource optimization or weather model. An explicit `basis` string accompanies findings to avoid interpreting a heuristic as prediction.

## Workflow state and durability

State keys are `kind`, `question`, `as_of`, `evidence`, `findings`, `draft`, `decision` and `status`. SQLite saves checkpoint versions under a server-generated UUID thread ID. A pending interrupt yields remaining nodes; the API reports `awaiting_approval` when `snapshot.next` is nonempty. Final state reports `approved` or `rejected`.

A decision contains the input Boolean/reason plus server-assigned reviewer and UTC timestamp. The approval node has no vendor call or other side effect before interruption. A process lock covers state reads and graph invocation, preventing two same-process decisions from advancing one pending review concurrently. SQLite WAL assists database access but does not provide a distributed application lock. One Uvicorn process is the supported deployment.

Checkpoint state is useful evidence of the local review lifecycle, but an administrator with filesystem access can alter/delete it. Immutable audit requirements need a dedicated append-only or tamper-evident design, identity, event versioning and retention controls.

## Connector extension contract

`ConstructionConnector` is a Python protocol with `list_records() -> list[dict]`. Both mock implementations return normalized fixture records with an integration marker. A real adapter should define versioned typed schemas before expanding this protocol; current dictionaries deliberately do not claim vendor compatibility.

A production read adapter needs OAuth/token refresh, scopes, project mapping, pagination, timeouts, retries with jitter, rate-limit handling, revision/deletion processing, validation, provenance and access filtering. A write adapter additionally needs an approved draft hash, idempotency key, external identity binding, sandbox contract tests, reconciliation, error classification and an outbox so retries cannot duplicate actions.

## Optional local model boundary

`app/generation.py` calls the configured local Ollama `/api/chat` endpoint only when `BUILDSIGHT_OLLAMA_MODEL` is set. It sends the question and retrieved sources, requires JSON claims with document IDs and exact quotes, bounds response size and checks source membership. Invalid output or transport failure returns the extractive baseline. Tests simulate valid output, invalid quotations and timeouts; no live model has been verified. Model claim entailment is not automatically checked. Evaluate relevance, supported-claim rate, abstention, adversarial robustness, latency and cost separately. Keep model text out of the approval authorization decision. The endpoint URL is a trusted operator setting, not a client-supplied destination.

## Configuration

| Setting | Default | Meaning |
|---|---|---|
| `BUILDSIGHT_API_KEY` | `local-demo-key` | Shared local reviewer key |
| `BUILDSIGHT_DB` | `state/buildsight.sqlite` | SQLite checkpoint file |
| `BUILDSIGHT_OLLAMA_MODEL` | unset | Enable optional synthesis using an installed local model |
| `BUILDSIGHT_OLLAMA_URL` | `http://127.0.0.1:11434` | Operator-configured Ollama endpoint |
| Run `as_of` | `2026-11-07` | Reproducible synthetic analysis date |

No vendor or model secrets are required. `.env` is ignored by git; Compose reads shell variables or a local `.env` for interpolation. Direct Uvicorn invocation requires environment variables exported in the shell.
