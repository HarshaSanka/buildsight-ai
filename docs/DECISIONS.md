# Architecture decisions

## ADR-001: Local synthetic vertical slice

**Decision:** use a bundled fictional project and run without cloud credentials. **Reason:** reviewers can reproduce end-to-end behavior immediately and inspect every source. **Tradeoff:** no evidence of real source access, scale or field adoption. **Revisit:** after approved sandbox access and defined data policy.

## ADR-002: Lexical extractive baseline

**Decision:** use TF-IDF/cosine retrieval and exact excerpts. **Reason:** deterministic, low cost, offline and easy to audit. **Tradeoff:** poor synonym recall and no model synthesis. **Revisit:** when an independent query set can measure semantic retrieval and grounded generation improvements.

## ADR-003: Real LangGraph approval lifecycle

**Decision:** implement specialist branches with a persisted interrupt/resume instead of pretending a status flag is orchestration. **Reason:** demonstrate recoverable human review. **Tradeoff:** versioned workflow state needs lifecycle management; specialists remain deterministic templates. **Revisit:** when model-assisted tasks have evaluated contracts.

## ADR-004: SQLite and one process

**Decision:** SQLite saver, WAL and one process lock. **Reason:** portable state recovery with minimal services. **Tradeoff:** no horizontally scaled workflow coordination. **Revisit:** before multiple workers or replicas, using production checkpoints, migrations and per-run distributed coordination.

## ADR-005: NetworkX relationships

**Decision:** explicit typed edges with downstream traversal. **Reason:** relationship reasoning is inspectable and useful even at small scale. **Tradeoff:** graph is reconstructed and not integrated into text ranking; no full GraphRAG. **Revisit:** when richer graph queries, provenance, access control and scale justify new storage.

## ADR-006: No live write actions

**Decision:** approval records an advisory disposition only. **Reason:** neither engineering authority nor vendor access is available, and approval semantics must be designed independently of text generation. **Tradeoff:** no automatic RFI response or schedule change. **Revisit:** after authenticated roles, signed/versioned approval, sandbox validation and idempotent action/outbox design.

## ADR-007: CI verifies and packages

**Decision:** GitHub Actions tests code/retrieval and builds/smoke-tests an image. **Reason:** portable delivery evidence without inventing a deployment target. **Tradeoff:** no cloud environment or registry release. **Revisit:** when an authorized hosting target, secrets and rollout/rollback policy exist.
