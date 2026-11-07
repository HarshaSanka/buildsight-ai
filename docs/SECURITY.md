# Security, data handling and limitations

## Data classification

Bundled data is entirely synthetic. No real Kokosing data, employee information, site geometry, vendor credentials, CLEAR-I content or private enterprise configuration is included. The service persists questions and workflow evidence/decisions in local SQLite; do not paste confidential project information into this demo.

## Threat model

| Boundary / threat | Current behavior | Required before shared or real-data operation |
|---|---|---|
| Unauthorized API access | Shared API key, constant-time comparison | SSO/OIDC, reviewer roles, key rotation and TLS |
| Cross-project leakage | One fixture project only | Tenant/project filters enforced before retrieval and graph traversal |
| Document prompt injection | Default no LLM; optional model has no tools and validates source IDs/quotes | Untrusted-source separation and adversarial model/tool tests |
| Source HTML injection | Browser displays JSON with `textContent` | Maintain safe rendering; review future rich text |
| Duplicate approval | Per-process lock and terminal-state check | Distributed per-run coordination and request idempotency |
| Forged reviewer | Server labels all valid-key users local-reviewer | Verifiable user identity and evidence-bound approval |
| Checkpoint tampering | Local file permissions only | Controlled DB access, encryption, immutable audit events |
| Data loss | Disk checkpointing and manual backup | Tested backups, restore drills, retention policy |
| Resource exhaustion | Request-length limits | Rate limits, quotas, bounded work, timeouts and observability |
| Unsafe field action | No action adapter or external write | Qualified review, formal authority model and scoped execution |
| Dependency compromise | Exact package versions, CI | Vulnerability scanning, SBOM, digest pinning and update process |

## Deployment boundaries

The default key is publicly documented. Keep the service local. Compose binds to loopback and the container runs as a non-root user. No HTTPS, SSO, authorization per document, CORS policy for a separate frontend, CSRF/session architecture, distributed lock, external audit sink or production secret manager is implemented. This is a deliberate portfolio scope, not an assertion that these controls are unnecessary.

## Construction authority

A software review cannot certify reinforcing design, constructability, safety, contractual response, schedule commitment or permission to perform field work. Actual project decisions require qualified professionals and authoritative project processes. The application has no capability to close a live RFI, modify a schedule or release a pour.

## Reporting

Do not place credentials, private construction records or personal data in public issues. If extending the repository with real systems, define a private reporting channel and access process before accepting confidential information. No security certification or production approval is claimed.
