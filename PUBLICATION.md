# Source publication

This repository retains the existing GitHub history and restores source from the
prepared Phase 3 publication snapshot plus the October development work.
See [docs/SOURCE_RECOVERY.md](docs/SOURCE_RECOVERY.md) for provenance and checks.

Only source, documentation, licenses, dependency lockfiles, icons and public test
fixtures belong in Git. Do not commit wallet data, credentials, private notes,
build caches or release executables. The two explicitly allowed wallet `.keys`
files are inherited public test fixtures.

Publish generated packages through versioned Releases with checksums after a clean
build and validation. This recovery is not a new binary release.
