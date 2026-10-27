# ForgeCoin source build status

## October desktop and explorer

The current Windows application is under `apps/desktop-tauri` and requires Node.js,
Rust/MSVC, C++ build tools and WebView2. Follow its README for dependencies.
First build `forged.exe` and `forge-wallet-rpc.exe` from this checkout, then provide
them as `src-tauri/binaries/forged-x86_64-pc-windows-msvc.exe` and
`src-tauri/binaries/forge-wallet-rpc-x86_64-pc-windows-msvc.exe` within that app.
Include any runtime DLLs required by your native toolchain in the final package.
These generated files are excluded from Git. A fresh package has not been validated
from this combined source snapshot.

The independent explorer is under `apps/explorer`; install its locked Python
dependencies and read its deployment notes. The deployment script is specific to
an existing host and must be reviewed before reuse.

## Native source

The source includes vendored dependency directories rather than Git submodules.
Pass `-DMANUAL_SUBMODULES=1` to CMake to skip the inherited submodule-history check.
A starting configuration, after installing the required compiler and dependencies:

```sh
cmake -S . -B build -DMANUAL_SUBMODULES=1 -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
```

These are configuration/build entry points, not a claim of a verified clean build.
The complete native build from this publication snapshot remains to be validated.
Dependencies and compiler choices differ by platform; the inherited `docs` and
`contrib/depends` material supplies reference information and may still say Monero.
For Windows, use the matching MSYS2/MinGW environment for the native build.

To avoid embedding local account names, build in a neutral directory and configure
supported GCC/Clang prefix-map flags for source/debug paths. Scan final executable
strings and symbols as well as package documents before public distribution.

The desktop wrapper has separate instructions in
[apps/desktop/BUILDING.md](apps/desktop/BUILDING.md). Build the daemon and wallet
from this tree before packaging. Do not substitute older patched release binaries
and describe them as builds of this commit.

## Windows native baseline verified 2026-10-25

The imported development-chain native source compiled daemon, CLI wallet and wallet
RPC with MSYS2 MinGW GCC 16.2.0 / CMake 4.4.3 / Ninja. Windows reports the processor
as `AMD64`; the inherited root passes that spelling through while RandomX checks
lowercase architecture names. Explicitly use `-DARCH_ID=x86_64` on this toolchain:

```sh
cmake -S . -B build -G Ninja -DMANUAL_SUBMODULES=1 -DARCH_ID=x86_64 -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTS=ON
cmake --build build --target daemon simplewallet wallet_rpc_server --parallel 2
```

Without that option the attempted build compiled native sources but failed at
link time with unresolved RandomX JIT functions. Reconfiguration with the option
built the omitted JIT sources and all three executables successfully. This is
build evidence for the imported native baseline, not FCMP/CARROT consensus,
runtime, clean-machine, signing or release evidence. `ARCH=native` output is
host-specific; portable release builds and independent reproduction are pending.
RPC functional tests were skipped during configuration because the selected
Python lacks requests, psutil, monotonic, zmq and deepdiff. Imported generated
version metadata still identifies Monero 0.18.5.1 as a release; correct branding
and release provenance must be addressed before packaging. See root STEP-008.
