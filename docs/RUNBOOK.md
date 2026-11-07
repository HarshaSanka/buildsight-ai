# Operations runbook

## Supported operating mode

Single Uvicorn worker on localhost, a small static synthetic corpus, shared demonstration key and SQLite checkpoint file. A live external system is never required. For production deployment planning, use the gaps in SECURITY.md rather than treating this runbook as enterprise certification.

## Start and readiness

1. Use Python 3.13, install `requirements.lock`, and run lint/tests.
2. Set `BUILDSIGHT_API_KEY` if replacing the demo key.
3. Start `uvicorn app.main:app --host 127.0.0.1 --port 8000` from repository root.
4. GET `/health`; expect status `ok` and synthetic/extractive mode.
5. Ask a known reinforcing-conflict query using the key; inspect citations.
6. Create a workflow, reject it and confirm a second decision returns 409.

Health checks confirm process liveness. They do not evaluate source freshness, retrieval utility or any vendor connection.

## Graceful stop and restart

Stop Uvicorn with Ctrl-C or stop the Compose service. Restart using the same database path/volume. Verify a known pending run by UUID and resume it. If using Compose, `down` retains the named volume; `down -v` removes it and all checkpoint data. Never delete state to fix an incident without preserving needed records.

## Backup and restore

For the simplest consistent backup, stop the service and copy the entire state directory, including any SQLite WAL/SHM sidecars. Alternatively, while running, use the SQLite online backup API to create a consistent database copy:

```bash
python - <<'PYBACKUP'
import sqlite3
from pathlib import Path
Path('backups').mkdir(exist_ok=True)
with sqlite3.connect('state/buildsight.sqlite') as source:
    with sqlite3.connect('backups/buildsight.sqlite') as target:
        source.backup(target)
PYBACKUP
```

Keep backups outside version control and under access control; add `backups/` to local exclusions if used. Restore into a separate test location first, run `PRAGMA integrity_check`, start with `BUILDSIGHT_DB` pointing to the restored copy, and verify a saved run. To replace active state, stop the service and preserve the existing state directory before restoring. Restoring an older backup can remove newer decisions; reconcile records before reuse.

## Incident playbooks

| Symptom | Likely cause | Diagnostic and resolution |
|---|---|---|
| HTTP 401 | Browser key differs from server environment | Check configured key without printing it to logs; re-enter it |
| HTTP 422 | Invalid kind/date or input length | Inspect generated schema and correct the request |
| HTTP 404 on run | Wrong UUID, database path or state volume | Compare saved ID/path; inspect mounted volume and restore history |
| HTTP 409 on decision | Run already approved/rejected | Read current state; create a new review for revised analysis |
| No relevant answer | Lexical vocabulary mismatch or missing evidence | Read corpus; add supported sources and evaluate retrieval before tuning |
| Unexpected high risk | Past start or near-term zero-float activity | Inspect `as_of`, start date, status and rule basis |
| SQLite locked | Multiple processes or external file contention | Stop extra workers; preserve state; restart one process |
| Permission denied | Database directory not writable | Correct ownership for the intended service user |
| Startup JSON failure | Invalid fixture edit | Revert or validate fixture; rerun tests |
| CI dependency install fails | Platform/Python incompatibility or package resolution | Compare Python 3.13 and lock; reproduce in a clean environment |

Do not respond to a source discrepancy by changing engineering instructions. Verify against the authoritative source with a qualified reviewer.

## Release procedure

Run lint, tests and evaluation. Review the synthetic-data boundary and diff for secrets or proprietary content. Commit code, data and guides together. Push a review branch or approved main change. GitHub Actions runs verification, image build and container health smoke test. Inspect the result before tagging a release. The current pipeline does not publish a registry image or deploy a cloud service.

Before updating dependencies, preserve the old lock and test database copy. Install in a fresh Python 3.13 environment, rerun behavior checks and verify restart compatibility. Changes to workflow state or node names may affect existing checkpoints; design migration or retire old runs explicitly.

## Rollback

Select the previously verified code commit and dependency lock. Stop the service. Back up current state. Restore the corresponding environment and compatible database copy if a state migration occurred, then restart on localhost and run the readiness sequence. Do not overwrite newer decisions silently. No vendor rollback is necessary in this version because no vendor writes exist.

## Monitoring and data retention

Use Uvicorn logs to investigate availability and HTTP errors. Avoid logging keys, complete source records or private questions in a future real-data environment. The current app has no metrics backend, alerts, retention scheduler or automated cleanup. For a portfolio demo, manually remove disposable state only after preserving desired evidence. For real data, define retention, deletion, access review and backup policy before ingestion.

## Demonstration checklist

- Confirm the screen clearly says synthetic, identifies its generation mode and discloses simulated vendor connections.
- Search for reinforcing conflict and read exact citations.
- Show graph blocker/predecessor edges.
- Start each specialist branch and explain its distinct draft.
- Reject one draft, approve another, and show duplicate rejection.
- Restart a pending run and complete it.
- Show evaluation limits and production gaps.
