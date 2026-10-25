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

## Source-matched wallet RPC build follow-up

Using the already configured disposable MinGW build with `ARCH_ID=x86_64`, `cmake --build build-disposable --target wallet_rpc_server --parallel 2` completed with exit code **0** and `[100%] Built target wallet_rpc_server`. No wallet process was started and no RPC was exposed.

The resulting `build-disposable/bin/forge-wallet-rpc.exe` is **34,279,313 bytes** with SHA-256 `34a3f72add57fb96beb3a822d28c910e1e6eadb2f6acfdee01a1a901de7b12e0`. Source checkout HEAD is `0f3a9a2820a6285838fb45227a34c65957615e38`; independently attested reproducibility remains outstanding. The existing `forged.exe` hash remains `600a76d02fbf9f46825ca989daf1c74187aa3bf524d651c35cfe6fbbc1fd2836`.

Running the hardened read-only preflight with both native binaries reports `FOUND` for daemon and wallet RPC, while desktop and XMRig remain `BLOCKED`, ending with exit code **1** and `NOT VALIDATED`. Structural PE checks do not verify runtime dependencies, address/chain correctness, signatures, or provenance.

**Packaging is still blocked:** Tauri expects `binaries/forged-x86_64-pc-windows-msvc.exe` and `binaries/forge-wallet-rpc-x86_64-pc-windows-msvc.exe`. The current artifacts are MinGW-built, not verified MSVC-target sidecars. Do not simply rename these artifacts to claim MSVC build provenance; audit compatibility and runtime dependency packaging first. No XMRig executable, network-isolated true share verifier, Solo/Pool mining, mature reward, or payout acceptance has been verified.

## Sidecar dependency audit and guarded staging follow-up

The previous paragraph describes the gate before this follow-up. Tauri's suffix
is a host artifact selection convention, not a claim about the sidecar compiler:
https://v2.tauri.app/develop/sidecar/ . These sidecars run as separate Windows
processes and do not link MinGW C++ objects into the MSVC Rust application.
They remain MinGW-built artifacts regardless of their packaging filenames.

Read-only inspection with `C:\msys64\mingw64\bin\objdump.exe -p` on each
native executable found the same imports: `ADVAPI32.dll`, `CRYPT32.dll`,
`IPHLPAPI.DLL`, `KERNEL32.dll`, `msvcrt.dll`, `MSWSOCK.dll`, `SHELL32.dll`,
`USER32.dll`, `WS2_32.dll`. No MinGW runtime DLL was listed. This supports
staging the exact reviewed bytes without shipping additional MinGW DLLs;
it does not prove clean-machine execution, dynamic LoadLibrary behavior,
minimum supported Windows version, or installer correctness.

`tools/stage_windows_sidecars.py` pins the two digests above and explicitly
records MinGW provenance and source commit. It validates the whole set before
writing, then writes the exact bytes it hashed. Other builds require a fresh
dependency/provenance review and digest update. From the repository root:

```powershell
python tools/stage_windows_sidecars.py --source build-disposable/bin --destination apps/desktop-tauri/src-tauri/binaries
```

Both the Windows Cargo build script and development staging script reject
missing/unreviewed artifacts. Only `x86_64-pc-windows-msvc` host packaging has
reviewed sidecars; other Windows targets fail closed. Python is now an explicit
Windows build prerequisite. Generated executables remain ignored and uncommitted.
This is a local packaging prerequisite, not reproducible-build attestation or
release approval. Keep staged files immutable during builds; concurrent mutation
after build-script validation is not prevented by a digest inventory guard.

Validation on TREYS_DELL_RTX:

- Six staging/preflight Python tests passed, including all-set refusal before
  writes and staged-artifact replacement detection.
- Offline locked desktop compilation succeeded with the reviewed sidecars.
  Rust library tests: four passed, two process-launching tests ignored.
- Thirteen Python RandomX input/protocol/ledger tests passed; these do not run
  native RandomX proof validation. Nine evidence-validator controls passed.
- PowerShell development staging completed after digest validation.
- Explicitly selecting the ignored mining test without the isolation
  acknowledgement failed immediately at its first assertion (Cargo exit 101),
  before directory creation, socket binding, or process launch. This intentional
  refusal is evidence of the guard, not a passing mining integration test.

The mining test now requires `FORGE_TEST_EGRESS_DENIED=externally-enforced`.
This is an operator acknowledgement only; it does not configure or verify OS
isolation. Do not set it on an ordinary connected host. Establish a disconnected
VM or independently tested non-loopback egress denial before any future launch.
The fixture is explicitly labeled protocol-only and still acknowledges shares
without native RandomX verification.

No XMRig candidate was supplied or found in the disposable checkout/build output.
No arbitrary installed miner or wallet locations were searched. Upstream documents
donation as disabled in source, and upstream `src/donate.h` sets the minimum to
one percent: https://xmrig.com/docs/miner and
https://github.com/xmrig/xmrig/blob/master/src/donate.h . The existing zero config
must not be treated as a no-egress guarantee. Pinned XMRig provenance, its actual
runtime dependencies/donation policy, OS isolation, native valid/invalid/stale
share verification, clean-machine installer execution, Solo/Pool block acceptance,
mature rewards and payouts remain unresolved. No mining, wallet, daemon, desktop
application, installer, public pool or chain service was launched in this follow-up.
