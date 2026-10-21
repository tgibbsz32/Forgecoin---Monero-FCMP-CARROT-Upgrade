# ForgeCoin governance API — development-only foundation

This service is **not deployed**, does not register real voters, and cannot accept binding election ballots. It is intended to run locally or in an isolated test environment. GitHub Pages cannot enforce voter eligibility.

## Requirements and start

Python 3.11+; install in a virtual environment:

```bash
pip install -r services/governance_api/requirements.txt
uvicorn services.governance_api.app:app --reload --host 127.0.0.1 --port 8765
```

The Python import-friendly directory is `services/governance_api` (underscore), not a production service. From the repository root, run tests with `python -m unittest services.governance_api.test_app`.

## API

- `GET /health`: dev status.
- `POST /auth/challenge` with `{"address":"<base58 Solana public key>"}`: creates a one-time nonce and a signed-message challenge (server-side generated).
- `POST /auth/verify` with `{"address":"...","nonce":"...","signature":"<base58 ed25519 signature>"}`: verifies the exact challenge with Ed25519, consumes nonce and returns an opaque session token.
- `GET /me` with `Authorization: Bearer <token>`: returns verified wallet and assigned demo roles.
- `GET /elections/{election_id}/eligibility` with bearer token: evaluates role at the server, not in browser JavaScript.

Member registration and reviewed role decisions now persist in SQLite. Set `FORGECOIN_GOVERNANCE_DB` to an isolated writable path (default: `governance-dev.sqlite3` in working directory). **Never commit the database or identity evidence.** `review_cli.py` provides a local-only administrator workflow; it is not an HTTP route. For example from repository root: `python -m services.governance_api.review_cli approve WALLET miner --reviewer reviewer-id --reason 'test evidence reviewed'`, or `python -m services.governance_api.review_cli revoke WALLET miner --reviewer reviewer-id --reason 'eligibility expired'`. Inspect decisions with `python -m services.governance_api.review_cli history WALLET`. CLI possession is a trust boundary: do not let untrusted users access the host, database, or its process. This prototype does not validate reviewer identity, attestations or reviewer quorum.

All new accounts start with **zero verified roles**. There is deliberately no public endpoint for self-awarding 'miner', 'developer', 'community', 'staking' or 'chamber' roles. Admin provisioning, uniqueness verification, mining proofs, stake snapshots, audited ballots, signed credentials and long-term persistence must be built and reviewed separately.

Security limitations: nonces and sessions are in **process memory** (lost on restart), while role decisions persist in SQLite. The CLI administrator can change roles directly without independent approval; this is not safe for production. SQLite here has no identity-verification workflow, review quorum, tamper-evident external audit anchoring or election credential issuance; it is not scalable or production-ready. No CORS origins are enabled. Sessions expire, challenges expire and are single-use, and payload sizes are bounded. Use HTTPS, CSRF-resistant authenticated sessions where appropriate, rate limits, durable atomic nonce storage, distributed abuse defense, admin audit logs and independently reviewed election logic before public operation. Do not bind to 0.0.0.0 on an internet-facing Oracle VM.

## Eligibility model

The sample elections are:
- `staking`: staking role (later require validated on-chain stake snapshot and election weight).
- `miner`: miner role (verified FRG mining contribution).
- `developer`: contributor role.
- `community`: verified unique community person.
- `chamber`: seated delegate credential.

A category credential may authorize access to an election **only after election-specific snapshots and anti-duplicate checks are introduced**. Endpoint results at this phase must not be used to cast or count ballots.

## Member eligibility application workflow (experimental)

Authenticated wallets may send `POST /applications` containing `role` (`miner`, `developer`, or `community`), `evidence_reference` (an opaque `ref:` reference or public HTTPS URL), and a short `statement`. The service records a **pending** application in SQLite and returns its ID; this grants **no** voting role. `GET /applications/mine` returns only the authenticated wallet's application IDs, roles, statuses and timestamps, and deliberately omits evidence and reviewer notes.

No HTTP route can approve an application. Authorized local administrators can *experimentally* review a pending application from the repository root with:

```bash
python -m services.governance_api.review_applications approve 1 --reviewer independent-reviewer --reason "Independently checked mining evidence"
python -m services.governance_api.review_applications reject 2 --reviewer independent-reviewer --reason "Inadequate documentary evidence"
python -m services.governance_api.review_applications audit 1
```

Reviewer CLI access is **not itself authenticated or independently approved**; do not deploy it to an untrusted host. Reviewer identity is a text claim. Review approval creates an audited role decision, but does not enable election ballots. The system prevents the applicant wallet string from being used as its own reviewer identifier; this alone is **not robust reviewer identity verification**. A production service requires managed reviewers, multiple-approval rules, secure private evidence storage, tamper-evident logs, retention/deletion policy, appeals, spam prevention and stronger uniqueness checks.

Only one pending application per wallet and constituency is accepted. Rejected/approved requests are retained in the audit database; follow-up resubmissions need a documented policy. **Do not upload passports, selfies, private keys, recovery phrases or sensitive identity documents to this API.** Prefer opaque evidence references that do not themselves reveal private evidence; references and statements are still stored in SQLite and must be treated as potentially sensitive.

Staking eligibility must eventually be determined by verified Solana stake snapshots, and chamber membership by a separately authenticated elected-seat registry. Neither can be requested using this application endpoint.

Run the local test suite from repository root:
```bash
python -m unittest services.governance_api.test_app
```
No public deployment or tests in CI have been verified as part of this change.
