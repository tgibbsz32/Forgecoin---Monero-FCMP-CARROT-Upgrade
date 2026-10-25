# STEP-003 — 2026-10-25 — FCMP++ source gate recovered and hardened

Files: native-frg/tools/fcmp_port_preflight.py, tools/test_fcmp_port_preflight.py, docs/FCMP_PORT_INTEGRATION.md; root offline CI extended. Imported attributable readiness source from old draft PR #100 at dcdde2c7571e2180ab81e9a173ccd395df0dba34. Fixed reference-error precedence; dirty/untracked reference checkouts and Git failures/timeouts now fail closed. Incorrect pins skip status inspection.

Implementation commit: 04ab1786786204805ee9d1a5b0c11af3a6a8de20. Parent STEP-002: 79a346209b15c6691093874e4d56d4cf9bd9aab9. This handoff is committed after completed work to record its exact SHA.

Commands/results: from native-frg, Python 3.13 venv: python -m unittest tools.test_fcmp_port_preflight apps.explorer.test_app services.pool_research.test_model -v — 26 passed (8 guard, 14 explorer, 4 accounting). Initial guard revision timed out inspecting temp directories even for wrong pins; corrected by short-circuiting incorrect pins and handling subprocess failures, then reran successfully. An incorrectly rooted unittest discover command failed imports; documented module invocation from native-frg succeeds.

python tools/fcmp_port_preflight.py --fork-root . --upstream-root TEMP/forgecoin-fcmp-upstream-beta3-20261025 --require-integrated — expected exit 2: staged ForgeCoin 0/11 surfaces, reference 11/11, clean pinned d80596ad18110390b6ca97a77e29aba36f4644c9 checkout. Presence is not cryptographic verification. git diff --check passed. No consensus changes or activation.

Native build investigation started separately: MSYS2 MinGW CMake 4.4.3 / GCC 16.2 configured the staged source successfully with -G Ninja -DMANUAL_SUBMODULES=1 -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON. Configuration warns RPC functional tests are skipped because selected Python lacks requests/psutil/monotonic/zmq/deepdiff. Compiling daemon/simplewallet/wallet_rpc_server is in progress; this is NOT a successful binary build claim. STEP-004 must record its actual result.

Blockers: complete FCMP++/CARROT port and native fork-version mapping, genesis proof, Windows/Linux/ARM64 builds and adversarial/integration tests, official pool implementation and paid-share evidence, packaging and staging still pending. Solana and utility implementation deferred. No production operations.

Next: finish native baseline build investigation, record failures and repair build-only compatibility if justified. Establish source identity invariants before importing any cryptographic consensus changes; keep protected local drafts untouched.
