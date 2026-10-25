# STEP-008 — 2026-10-25 — native Windows baseline build resolved

Documentation commit: e446e97352288d2dc21e2343d8b358e2bb8b8bb7. Files: native-frg/BUILDING.md and this handoff. Actual native sources were compiled from the separate work/native-frg checkout, whose native-frg/src tree ec05651c7eba02c8551730be9465e7f1d117b938 exactly matches old source abd29371abf70dcebcddaf76c0788040f38871a6:src. It excludes the separately imported FCMP backend, so this is baseline native build evidence only.

Initial command: cmake -S native-frg -B ../native-build -G Ninja -DMANUAL_SUBMODULES=1 -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON; cmake --build ../native-build --target daemon simplewallet wallet_rpc_server --parallel 2. Sources compiled, but linking failed with unresolved randomx::JitCompilerX86 symbols. Diagnosis: root passes detected AMD64 to RandomX, which recognizes lowercase amd64/x86_64; x86 JIT sources were omitted.

Resolution: reconfigured with the same options plus -DARCH_ID=x86_64; rebuilt the same three targets. Added JIT sources; all three linked successfully, exit 0. No consensus/economic/identity change or source replacement was needed. Toolchain: MSYS2 MinGW GCC 16.2.0, CMake 4.4.3, Ninja on Windows x64.

Local artifact evidence (not release downloads):

[
  {
    "name": "forge-wallet-cli.exe",
    "bytes": 34957116,
    "sha256": "f9cc2752e0aae298f2d824d392229cb687a8404e6808d86df7fb92cac44e45b9"
  },
  {
    "name": "forge-wallet-rpc.exe",
    "bytes": 34289041,
    "sha256": "682f3a1793956ce16b3a96f7a753807c6f51ed4e1e710c115ce402714a726556"
  },
  {
    "name": "forged.exe",
    "bytes": 33921568,
    "sha256": "c2d76a66fbb3589746e5c7a2bd125eb3a0b84dafa215c2aac07d45b4888252c9"
  }
]


objdump -p on daemon and wallet RPC showed imports from ADVAPI32, CRYPT32, IPHLPAPI, KERNEL32, msvcrt, MSWSOCK, SHELL32, USER32 and WS2_32. This import-table check does not establish runtime portability, supply-chain approval or package completeness. No daemon or wallet was started; no mining/network/funds operation occurred. Binaries remain intermediate files in work/native-build/bin and were not staged as Tauri sidecars or distributed.

Warnings/remaining gates: configuration skipped RPC functional tests because selected Python lacks requests/psutil/monotonic/zmq/deepdiff. Compiler emitted warnings, including legacy Boost use and inherited source diagnostics; no warning-free or audited-build claim. Default ARCH=native output is host-specific. Generated version.cpp still labels Monero 0.18.5.1/release, which needs correct branding/provenance before packaging. Source paths may be embedded. Independent reproducibility, Linux/ARM64 full builds, runtime and clean-machine tests, binary license audit, signing and packaging remain pending.

Protocol evidence remains separate: actual FCMP backend and full membership/SAL/FFI tests are in d7fbffd2d957f959533ad0e498cf5e25a6813a03 and PR https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/pull/6 . Remote protocol CI was still running at this handoff creation. Backend success does not mean daemon acceptance or CARROT wallet support.

Next: native proof wrappers and bounds validation; persistent tree/transaction serialization and Forge-specific fork mapping; consensus/mempool/P2P/RPC and CARROT scanning/signing/restore/wallet integration. Do not divert into pool/frontend utilities until protocol port progresses. Preserve both original local checkouts. Explicit owner authorization remains required for critical consensus merges or production activation; Solana/SPL/swaps/dark pool remain deferred.
