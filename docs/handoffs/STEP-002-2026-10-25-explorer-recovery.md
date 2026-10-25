# STEP-002 — 2026-10-25 — recover scratch explorer/accounting work

Completed: copied only apps/explorer/app.py, apps/explorer/test_app.py and services/pool_research/test_model.py from TEMP/forgecoin-launch-work-20261025 into native-frg/. Originals remain untouched. RPC payload hardening and tip-aware caches recovered; accounting test now uses a package-relative import. Added a root offline-only CI workflow (no inherited deployment workflow enabled).

Commands/results: created a test venv outside Git; installed Flask==3.1.3; from native-frg ran python -m unittest apps.explorer.test_app services.pool_research.test_model -v: 18 passed (14 Flask + 4 accounting), Python 3.13 on Windows. git diff --check passed. These are mocked/offline tests; no live daemon/payout/100-worker load result is implied. Remote CI is pending at handoff creation.

Implementation SHA: 4cc914a3b2218cb9bacf109ceb89d0ca725a6a4a. CI SHA: 686986316de93f65324459e96710d20d6225d2c9. Parent handoff: 901a2f08299cd07b958c17e5c5539b206d5b210f. Migration PR: https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/1. This handoff is a subsequent commit so exact completed work SHAs are recorded.

Review limits/blockers: fixtures do not validate every possible malformed header/info/transaction shape; further fail-closed response validation and live isolated integration remain necessary. Mempool membership can change without tip/count changes, so short cached tx status can be stale. TLS/hosting and production launch remain blocked. No consensus source changed; protected local checkout remains untouched. Solana/utilities deferred.

Next: import PR #100's pinned read-only source guard with provenance, fix any fail-closed precedence defects, test, then establish explicit native build/consensus integration gates.
