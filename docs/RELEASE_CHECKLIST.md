# ForgeCoin public release checklist

## Source publication
- Publish only this repository directory, never the surrounding workspace.
- Inspect staged files and the complete Git history for private data.
- Verify author identity before every commit; the repository uses a project identity.
- Keep third-party license notices and public test fixtures.
- Enable a private security-reporting channel on the chosen hosting account.

## Binary releases
- Build native binaries from the exact source commit being released.
- Vendored dependencies are included; configure CMake with `-DMANUAL_SUBMODULES=1`.
- Validate the native build on each supported platform before claiming support.
- Verify genesis, network UUID, v16 activation at height 1 and monetary constants.
- Test daemon startup, two-node synchronization, wallet recovery and transfers.
- Test mining start/stop, address creation, explorer and desktop resizing.
- Check compiled binaries for personal build paths and debug information.
- Do not change genesis or restore inherited Monero checkpoints or seed nodes.
- If including XMRig, include its matching source and license.
- Keep signing private keys outside the repository. Public signatures can identify
  or correlate a release signer; choose the intended public identity deliberately.
- Generate checksums after final packaging/signing; publish binaries as release assets.
- Describe known limitations, bootstrap peer requirements and upgrade instructions.

## Validation status
This source export has not received a fresh full native rebuild or independent
security audit. Earlier desktop tests used packaged Phase 3 native binaries.
The testnet and stagenet identities are not ready for public use.
