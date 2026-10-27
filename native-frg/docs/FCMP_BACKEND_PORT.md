# FCMP++ actual backend port — increment 1

This branch builds actual FCMP++ proof code. It does not activate it in daemon
consensus, serialize new FRG transactions, or implement CARROT wallet scanning.

## Provenance and licenses

`src/fcmp_pp/fcmp_pp_rust/` was imported from seraphis-migration/monero commit
`d80596ad18110390b6ca97a77e29aba36f4644c9` (beta 3.1), under the retained Monero
BSD license and source-header notices. Cargo.toml, Cargo.lock, fcmp++.h and the
upstream CMake file are retained. The sole change to imported lib.rs appends the
test-module declaration; backend_tests.rs is additional port testing.

The full proof fixture is adapted from monero-oxide's
`monero-oxide/ringct/fcmp++/src/tests/mod.rs` at
`31c26d96eaadbba910ffe3613ad8b4cf9c598a93`, by Luke Parker. Its MIT license is
included as `src/fcmp_pp/fcmp_pp_rust/LICENSE-monero-oxide`. The fixture adds native
FFI roundtrip, changed-message, wrong-root and malformed-proof rejection.
Cargo's lock preserves transitive source checksums and Git revisions, including
crypto-bigint `78352771313f1e9b8e48abe5ce30d50d6bdd291d`. Always use `--locked`;
review all dependency licenses/notices again before binary distribution.

## Build and test

From native-frg, with MinGW GCC/Ninja and Cargo on PATH, and Rust's
x86_64-pc-windows-gnu standard library installed:

    cmake -S . -B ../fcmp-build -G Ninja -DMANUAL_SUBMODULES=1 -DBUILD_TESTS=OFF -DFORGE_BUILD_FCMP_BACKEND=ON
    cmake --build ../fcmp-build --target forge_fcmp_backend_ffi --parallel 2
    ctest --test-dir ../fcmp-build -R '^forge_fcmp_backend_ffi$' --output-on-failure
    cargo test --locked --manifest-path src/fcmp_pp/fcmp_pp_rust/Cargo.toml --target x86_64-pc-windows-gnu --lib -j 2

Unix builds use Rust's host target; Windows currently requires MinGW. The
CMake test target is opt-in and deliberately not linked into the production
daemon yet. Do not mistake it for a protocol activation flag. CMake uses an
isolated Cargo output directory; optionally set FORGE_FCMP_CARGO_TARGET_DIR.

## Exact verified boundary

Windows x64: Rust static backend compiled; C ABI test passed with a valid SAL
proof and tampered-message/proof/key-image and wrong-opening rejection; generator
encoding roundtrips and noncanonical scalar rejection passed. Full membership +
SAL proof generation/serialization/native FFI verification passed, with changed
message, wrong tree root and malformed-proof rejection. These are single-input,
single-layer fixtures, not a full protocol or adversarial audit.

## Next protocol increments (implementation order)

1. Native C++ crypto/FFI wrappers, proof types and safe length/count validation;
   retain historical verifiers and do not equate marker presence with integration.
2. FCMP transaction and block serialization plus persistent curve-tree state;
   deterministic output ordering, append, sync, restart and reorg rollback.
3. Forge-specific version dispatch across main/alternate-chain validation,
   mempool, block templates, relay/P2P and daemon RPC. Do not reuse Monero v17/v18
   activation rules: FRG v17-v19 already has different meanings.
4. CARROT shared crypto dependencies, output types, construction, scanning,
   subaddresses, restore, view-only behavior, signing and wallet RPC. Then Tauri.
5. Independent full-node/wallet integration and malformed-proof/inflation/replay
   tests, Windows/Linux/ARM64 agreement, independent review and release gates.

No chain identity, genesis, monetary policy, difficulty schedule or protected
local drafts were changed by this increment. Production merge/activation and
all Solana/SPL/swaps/dark-pool work remain excluded.
