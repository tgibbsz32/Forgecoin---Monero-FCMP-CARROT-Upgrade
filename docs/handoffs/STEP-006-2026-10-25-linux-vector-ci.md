# STEP-006 — 2026-10-25 — repair Linux vector CI dependencies

Completed: diagnosed first Linux vector run 40239982605 using its actual job log. Compilation lacked boost/multiprecision/cpp_int.hpp and sodium/crypto_verify_32.h; it had not executed the vectors. Added explicit libboost-dev and libsodium-dev installation to .github/workflows/native-consensus-vectors.yml in commit 5e2fd2a37fcd85eec7284a2a59cfc17d4af4b3a4.

Verification: rerun passed at https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40240043023 . Together with STEP-005 this establishes current native difficulty vectors on Windows x64 and Linux x64, not ARM64 or FCMP/CARROT verification. This handoff follows the completed fix; exact handoff SHA is in Git history.

Native baseline daemon/wallet compilation is still running; no binary-build claim yet. Owner steering now explicitly prioritizes actual FCMP/CARROT implementation over additional peripheral checks. Next: use an isolated port worktree so ongoing baseline compilation cannot consume changing source; begin the actual pinned cryptographic backend and build integration, then propagate through serialization, curve-tree persistence, consensus, mempool/RPC and CARROT wallet paths. Keep source identity/economics and protected local drafts intact. No production activation, merge or funds operations.
