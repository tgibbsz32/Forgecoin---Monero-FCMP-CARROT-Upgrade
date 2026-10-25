# Isolated desktop mining follow-up, 2026-10-25

PR #89 is merged at `0f3a9a2820a6285838fb45227a34c65957615e38`.
Work used a fresh disposable clone of that commit. The original development
checkout, application settings and real wallets were not inspected or changed.
No daemon, wallet RPC, desktop or XMRig process was launched. No live mining,
wallet, pool or chain services were contacted. GitHub was used for source and PRs.

## Read-only preflight review

The previous implementation accepted the two bytes `MZ` as a Windows PE file.
The follow-up checks the DOS header, bounded PE offset, PE signature, x64 machine,
executable/non-DLL flags, PE32+ optional header, section count/table bounds and
raw section extents, and handles unreadable files as BLOCKED. Hashing uses the
same read-only file handle. SHA-256 is an inventory value, not provenance proof.
This is a bounded structural sanity check, not a complete Windows loader,
signature verifier, source attestation or guarantee that a file is safe to run.
Synthetic positive fixtures must never be described as actual mining binaries.

Before running candidates, independently bind each digest to an exact source
commit/build recipe or trusted upstream release evidence, account for runtime
DLLs and establish OS-level network isolation. Do not execute arbitrary files
merely because this preflight prints FOUND. Concurrent file mutation and later
replacement are outside this inventory check; use immutable staged artifacts.

## Acceptance blockers identified by source review

- No executable candidates are tracked in the fresh clone. Older archived
  development binaries are not evidence of a build of this commit and were not
  searched for in the original checkout or application directories.
- The normal Tauri desktop defaults include a public peer and a persistent
  application data directory. Launching the UI as-is is not an isolated test.
- `offline_mining_compatibility` is ignored by default. Its Solo daemon arguments
  include offline mode and a disposable directory, but its Pool portion calls
  the normal `start_pool` launcher. That launcher does not override XMRig's
  donation policy. The earlier direct XMRig Solo test explicitly sets donation
  level zero; that does not carry over to the subsequent Pool config. Do not
  run this integration test under a no-live-services constraint without an
  independently verified egress-denied environment and reviewed miner policy.
- The local Stratum fixture checks method/job ID and replies OK; it does not
  independently verify RandomX proof of work, invalid/stale rejection, reward
  crediting or matured payouts. It cannot establish the Pool V1 release gate.
- Windows private template persistence remains disabled, with its refusal test
  passing. Do not enable it as a workaround for mining acceptance.

## Reproduction and tests

From the disposable repository root:

```powershell
python -m unittest tools.test_preflight_desktop_mining services.pool_research.test_private_capture -v
python tools/validate_desktop_mining_evidence.py --self-test
python -m unittest services.pool_research.test_randomx_validation services.pool_research.test_stratum_protocol services.pool_research.test_ledger -v
python services/pool_research/test_model.py
```

Preflight/private-capture run: 8 tests, 5 passed and 3 POSIX-only skips. Preflight
includes 16 malformed synthetic PE cases, missing/unreadable paths, unchanged
input bytes, SHA-256 and CLI exit-status checks. Evidence validator: 9 controls
passed. RandomX input validation, Stratum parsing and ledger: 13 passed.
Accounting model: 4 passed when invoked as its standalone script. An initial
module-based invocation of the model failed because it imports `model` locally;
this was an invocation issue, not a passing test, and was corrected as above.

No functional Solo/Pool acceptance or verified mining binaries are claimed.

## Disposable build attempts

Native configuration succeeded using the installed MSYS2 MinGW64 toolchain
(CMake 4.4.3, GCC 16.2.0, Boost 1.92.0):

```powershell
$env:PATH = 'C:\msys64\mingw64\bin;' + $env:PATH
cmake -S . -B build-disposable -G 'MinGW Makefiles' -DMANUAL_SUBMODULES=1 -DCMAKE_BUILD_TYPE=Release
cmake --build build-disposable --target daemon wallet_rpc_server --parallel 2
```

The offline locked desktop test compilation was attempted with:

```powershell
cargo test --offline --locked --manifest-path apps/desktop-tauri/src-tauri/Cargo.toml --lib --no-run
```

It failed in the Tauri application build script because
`binaries/forged-x86_64-pc-windows-msvc.exe` does not exist. No stub sidecars were
supplied, and no Rust tests ran. Dependencies were available in the local cache.


## Recovered native build outcome and architecture correction (2026-10-25)

The initial MinGW native build **failed at daemon link** with unresolved RandomX x86 JIT symbols (`JitCompilerX86::generateProgramLight`, `enableWriting`, `enableExecution`, and related symbols). Investigation found that the generated RandomX build rules omitted `jit_compiler_x86.cpp` for this configuration.

Reconfiguration with `-DARCH_ID=x86_64` caused the generated RandomX build rules to include the missing JIT compilation unit. A targeted rebuild completed with exit code **0** and `[100%] Built target daemon`:

```powershell
$env:PATH = 'C:\msys64\mingw64\bin;' + $env:PATH
cmake -S . -B build-disposable -G 'MinGW Makefiles' -DMANUAL_SUBMODULES=1 -DCMAKE_BUILD_TYPE=Release -DARCH_ID=x86_64
cmake --build build-disposable --target daemon --parallel 2
```

Source checkout commit: `0f3a9a2820a6285838fb45227a34c65957615e38`.
Generated file: `build-disposable/bin/forged.exe`, **33,919,520 bytes**.
SHA-256: `600a76d02fbf9f46825ca989daf1c74187aa3bf524d651c35cfe6fbbc1fd2836`.

The hardened PE preflight identifies this daemon as structurally valid, with the explicit note that provenance is not independently verified. The command still exits without acceptance when the desktop, wallet-RPC, and XMRig candidates are absent. Preflight unit tests: **4 passed** when invoked from the repository root with `py -m unittest tools.test_preflight_desktop_mining -v`.

**Gates still blocked:** This MinGW-built executable is not yet a verified Tauri `x86_64-pc-windows-msvc` sidecar package; wallet-RPC and XMRig candidates remain unverified; no controlled egress sandbox has been established; the current mock pool acknowledges shares without validating native RandomX; neither Solo nor Pool integration, chain block acceptance, mature rewards, or payouts have been tested. Do not use this evidence as release approval. Do not commit the `build-disposable/` directory or generated executables.
