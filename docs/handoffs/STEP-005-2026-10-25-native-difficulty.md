# STEP-005 — 2026-10-25 — independent native difficulty regression

Files: .github/workflows/native-consensus-vectors.yml. Existing consensus and test sources remain unchanged. Added an offline Linux CI job that generates independent Python reference vectors outside the source tree and compiles the native C++ difficulty checker with assertions enabled (no NDEBUG).

Completed implementation commit: b11b21aac837bd97be6771ec6bc21085117ed181. Parent STEP-004 handoff: 0e38bebfcf76fc6d053be74ed7a77014b2dcd62f. This subsequent handoff records exact completed work.

Commands/results on Windows: copied tests/forgecoin/make_vectors.py, difficulty_model.py and historical-headers.json into work/difficulty-baseline, ran Python make_vectors.py (1,231 vectors). Used C:/msys64/mingw64/bin/g++.exe -std=c++17 -O2 -I native-frg/src -I native-frg/contrib/epee/include -I native-frg/external/easylogging++ native-frg/tests/forgecoin/lwma-consensus-test.cpp native-frg/src/cryptonote_basic/difficulty.cpp -o ../difficulty-baseline/lwma-consensus-test.exe. Executed that standalone checker with generated lwma-vectors.txt: 1231 consensus vectors passed, exit 0. No daemon or mining invoked.

Scope: current imported development-chain difficulty, including historical blocks, heights 499/500/599/600/699/700/701, mainnet/non-mainnet dispatch, timestamp normalization/overflow, suffix/full-history agreement and wide cumulative work. Does not validate the separate uncommitted fresh-candidate policy, FCMP++, CARROT, network transport, wallet restore, or ARM64.

Other verified evidence: Windows desktop frontend CI passed at https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40239896837 . New vector CI pending at handoff creation. Full daemon/simplewallet/wallet_rpc_server compilation remains in progress; this handoff does not declare a successful native binary build.

Next STEP-006: resolve full native build and record output, source hash, toolchain, warnings, failures and packaging limitations. Then begin explicitly mapped FCMP/CARROT source integration without importing old local consensus drafts or silently changing network identity. All launch and independent review gates remain pending. Solana/SPL/swaps/dark pool deferred.
