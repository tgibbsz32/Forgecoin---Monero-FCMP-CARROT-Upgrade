# STEP-009 — 2026-10-25 — continuation handoff

## Start here

**Exclusive project destination:** https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade . Continue actual FCMP++/CARROT implementation; the owner explicitly corrected the earlier emphasis on readiness checks and peripheral work. Do not describe a source guard or backend fixture as network-wide integration.

Active port checkout:
`C:/Users/tgibb/Documents/Codex/2026-10-25/referenced-chatgpt-conversation-this-is-an-3/work/fcmp-protocol-port`

Branch: `codex/fcmp-carrot-native-port-20261025`.
Last verified local/remote head before this handoff: `cf7f31fc5e27d6f002b614790950240062b8105e`.
Native source/build working directory inside checkout: `native-frg/`.
Active draft PR: https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/6 .
Destination main still points to original `34392d39ee31ee227d72c1720483015739041ec1`; nothing has been merged. This handoff is a subsequent commit, so obtain its own SHA from Git history rather than expecting a self-referential SHA in this file.

## Completed work and PR stack

| PR | Result | Branch |
| --- | --- | --- |
| [1](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/1) | Exact source snapshot under native-frg/, original destination README retained, licenses/notices and both histories preserved | codex/native-frg-migration-20261025 |
| [2](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/2) | Recovered explorer hardening, 14 Flask tests, accounting import fix and four accounting tests | codex/native-frg-explorer-recovery-20261025 |
| [3](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/3) | Old PR #100 source guard recovered and hardened; eight guard tests; not protocol implementation | codex/native-frg-fcmp-readiness-20261025 |
| [4](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/4) | Desktop Vite lock updated 8.3.1 to 8.3.5; frontend build/audit checks | codex/native-frg-build-baseline-20261025 |
| [5](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/5) | 1,231 existing native difficulty vectors; Linux header-dependency CI repair | codex/native-frg-consensus-vectors-20261025 |
| [6](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/6) | Actual pinned Rust FCMP++ proof backend, opt-in CMake target, native C ABI and full membership/SAL tests | codex/fcmp-carrot-native-port-20261025 |

PRs are stacked in order. Source migration commit `43e7f7a9d16f1705082877ba6ee7efa3604397a2` has destination and old source `abd29371abf70dcebcddaf76c0788040f38871a6` as parents; imported tree equality was checked. Actual backend implementation commit: `d7fbffd2d957f959533ad0e498cf5e25a6813a03`. STEP-001 through STEP-008 contain per-step files, commands, results, repaired failures and SHAs.

## Actual protocol implementation boundary

Pinned Monero reference: `seraphis-migration/monero`, beta 3.1, commit `d80596ad18110390b6ca97a77e29aba36f4644c9`. Existing clean reference checkout is TEMP/forgecoin-fcmp-upstream-beta3-20261025; reverify it before reuse. Imported backend is at `native-frg/src/fcmp_pp/fcmp_pp_rust/`. Preserve its Monero notices, Cargo lock and MIT monero-oxide attribution/license. Dependency revision: monero-oxide `31c26d96eaadbba910ffe3613ad8b4cf9c598a93`; crypto-bigint lock resolves `78352771313f1e9b8e48abe5ce30d50d6bdd291d`.

Actual implementation/build files:

- native-frg/cmake/ForgeFcmpBackend.cmake and inclusion from native-frg/CMakeLists.txt.
- native-frg/src/fcmp_pp/fcmp_pp_rust/{Cargo.toml,Cargo.lock,fcmp++.h,src/lib.rs,src/backend_tests.rs,LICENSE-monero-oxide}.
- native-frg/tests/fcmp_port/backend_ffi.c.
- .github/workflows/fcmp-backend.yml.
- native-frg/docs/FCMP_BACKEND_PORT.md.

**Working:** static proof backend; real SAL generation/verification through C; full one-input/one-layer membership+SAL proof generation, serialization, parsing and verification through FFI. Changed message, wrong tree root, malformed proof, changed SAL/key image and incorrect opening are rejected by exercised cases. Curve encoding and noncanonical-scalar cases pass.

**Not implemented:** daemon FCMP transaction acceptance, canonical new transaction/block formats, persistent curve-tree lifecycle, reorg rollback, new mempool/relay/RPC handling, CARROT scanning/signing/restore or Tauri support for new outputs. Backend CMake option FORGE_BUILD_FCMP_BACKEND defaults OFF; it is a development build option, not an activation rule. Source presence is not correctness. Preserve historical CLSAG/ring verification.

## Verification evidence

- Windows: 26 offline Python tests passed (8 source guard, 14 Flask, 4 accounting). [Linux CI](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40239781475) passed.
- Windows desktop frontend: TypeScript/Vite build passed; npm audit reported zero known vulnerabilities after update. [Windows CI](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40239896837) passed. No Tauri installer claim.
- Existing difficulty: 1,231 C++/independent-Python vectors passed on Windows and [Linux CI](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40240043023). Initial Linux run lacked Boost/sodium headers; repaired. No fresh-candidate/ARM64 claim.
- Actual protocol backend: Windows GNU Cargo build, CMake C ABI target/CTest, and full-proof Rust test passed. [Linux protocol CI](https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40240573970) passed all three stages. Tested code head dc78411ad3ad080fb9b710d73a6f5a7783ab98e0; subsequent commits through cf7f31f are documentation only.
- Imported baseline daemon/CLI wallet/wallet RPC compiled on Windows MinGW after adding -DARCH_ID=x86_64. This build excludes the separate FCMP backend. Artifact hashes, DLL imports and warnings are in STEP-008. No node/wallet was run.

From native-frg/, reproduction commands (adjust output paths deliberately):

```text
../../test-venv/Scripts/python.exe -m unittest tools.test_fcmp_port_preflight apps.explorer.test_app services.pool_research.test_model -v
cargo test --locked --manifest-path src/fcmp_pp/fcmp_pp_rust/Cargo.toml --target x86_64-pc-windows-gnu --lib -j 2
cmake -S . -B ../../fcmp-port-build -G Ninja -DMANUAL_SUBMODULES=1 -DBUILD_TESTS=OFF -DFORGE_BUILD_FCMP_BACKEND=ON
cmake --build ../../fcmp-port-build --target forge_fcmp_backend_ffi --parallel 2
ctest --test-dir ../../fcmp-port-build -R '^forge_fcmp_backend_ffi$' --output-on-failure
```

Put C:/msys64/mingw64/bin on PATH for the GNU build. Installed Rust targets include x86_64-pc-windows-gnu and MSVC; current backend integration was verified with GNU. Existing shared intermediate output directories under the task's work/ are fcmp-rust-build, fcmp-port-build, native-build and difficulty-baseline. Set CARGO_TARGET_DIR/FORGE_FCMP_CARGO_TARGET_DIR if deliberately reusing the first. Logs: fcmp-rust-build.log, fcmp-rust-tests.log, native-build-output.log (initial failure), native-reconfigure.log and native-build-retry.log (successful retry). No tracked generated binaries.

## Preserve these separate local states

- Baseline checkout work/native-frg is clean on codex/native-frg-consensus-vectors-20261025. It was the source directory for the native baseline build; keep it distinct from protocol port work.
- C:/msys64/home/tgibb/forgecoin: DO NOT change, reset, clean, stash or cherry-pick its drafts. Current read-only status still shows four modified files (cryptonote_format_utils.cpp, blockchain.cpp, hardforks.cpp, wallet2.cpp), untracked forgecoin_difficulty.h and tests/forgecoin/. These are separate consensus work.
- TEMP/forgecoin-launch-work-20261025: originally had three uncommitted explorer/accounting changes, copied into PR #2 without modifying originals. **At this handoff inspection it now reports clean**, on launch/explorer-hardening-and-readiness-20261025 at abd2937, and test_app.py is not tracked. The reason for this external-state difference was not established; do not claim original drafts are still present or restore/reset the checkout. The recovered changes remain committed in the new repository (4cc914a3b2218cb9bacf109ceb89d0ca725a6a4a).

## Immediate next implementation work

1. Continue on the isolated protocol branch, inspecting exact upstream APIs. Implement native C++ proof/FFI wrappers with ownership, length/count validation and rejection tests; avoid exposing raw unsafe FFI to untrusted transaction data.
2. Port coherent FCMP transaction/block proof types and serialization, then deterministic persistent curve-tree append/history/sync/restart/reorg behavior. Test actual proof acceptance and rejection against tree state.
3. Explicitly map ForgeCoin fork versions before wiring acceptance: existing FRG v17/v18/v19 represent difficulty changes, whereas Monero beta uses those versions differently. Preserve FRG identity, genesis, economics and existing-chain historical verification; do not copy upstream activation constants blindly.
4. Integrate main/alternate-chain validation, mempool, block templates, P2P relay and daemon RPC; exercise replay, malformed proofs, invalid roots, duplicate spends, amount conservation and reorgs on isolated networks.
5. Port CARROT shared crypto dependencies (including pinned mx25519 dependency), output construction, wallet scanning, view-only restore, subaddresses, signing and wallet RPC; then integrate the desktop. Do not merely copy source directories and claim support.
6. Independent Windows/Linux/ARM64 node/wallet integration and review precede packaging/staging/launch readiness. Write and COMMIT a new dated numbered handoff after each completed increment; include actual files, commands, results, SHAs, blockers and next work.

## Remaining release blockers and scope

Genesis permanent-unspendability proof remains unresolved; owner policy is in native-frg/docs/OWNER_POLICY_DECISIONS_2026-10-24.md. Pool/explorer obligations are in native-frg/docs/POOL_EXPLORER_IMPLEMENTATION_PLAN.md. Official 1% pool still needs actual Stratum/share validation, durable accounting, mature/reorg-safe payout implementation and two-miner payment evidence; research accounting is not a pool or payout service. Pool site, standalone observer, explorer node integration/TLS, hosting, signed packages and operational rehearsals remain unfinished.

Baseline build skipped RPC functional tests due to missing Python modules; version metadata still claims Monero 0.18.5.1 release; native-host CPU tuning, warnings, embedded paths and binary license obligations need release work. Backend tests do not establish a completed FCMP/CARROT port or cryptographic audit.

Defer ALL Solana/SPL/atomic-swap/dark-pool utility implementation until after native FRG launch. Do not deploy production, merge critical consensus changes, create/mint/transfer assets, start mainnet mining or move real funds without explicit owner authorization. No such action has been taken in this workflow.

## Handoff-only validation for this step

Inspected active branch/head/log and clean status; destination remote main and port branch refs; previous handoff; baseline and protected/scratch statuses; existing test/build logs and their locations. No implementation changed and no tests were rerun for this documentation-only step. Commit this file and push the existing protocol branch; its commit becomes part of PR #6.
