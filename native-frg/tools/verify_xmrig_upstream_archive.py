#!/usr/bin/env python3
"""Read-only SHA-256 check for the named upstream XMRig 6.26.0 Windows archive.

This does not run the archive/executable, establish trust in the publisher,
verify signed manifests, or authorize shipping a miner. Custom source builds
require separate source/build/provenance review.
"""
import argparse
import hashlib
from pathlib import Path

ARCHIVE_NAME = "xmrig-6.26.0-windows-x64.zip"
# Digest recorded in ForgeCoin issue #95 for the corresponding upstream release.
# Independently authenticate the upstream checksum list before trusting it.
EXPECTED_SHA256 = "bba8097cb37d9b458a1cb1137876b27cde6740d17fe4ccbc086ba07d87d9e147"


def inspect(path: Path, expected_sha256: str = EXPECTED_SHA256) -> tuple[bool, str]:
    path = Path(path)
    if path.name != ARCHIVE_NAME:
        return False, "unexpected archive filename (not the pinned upstream asset)"
    if path.is_symlink() or not path.is_file():
        return False, "missing, unreadable or symbolic-link archive"
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError:
        return False, "archive read failed"
    observed = digest.hexdigest()
    if observed != expected_sha256:
        return False, f"checksum mismatch: observed SHA-256 {observed}"
    return True, f"checksum matches recorded upstream digest: {observed}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", required=True, type=Path,
                        help="Path to pinned XMRig upstream release archive; never executed")
    args = parser.parse_args()
    verified, reason = inspect(args.archive)
    print(("MATCH " if verified else "BLOCKED ") + reason)
    if not verified:
        print("Do not run, stage, bundle or redistribute this unverified archive.")
        return 1
    print("Digest match only; authenticate the publisher and checksum list independently.")
    print("Do not equate a matching ZIP digest with miner policy, runtime or FRG compatibility.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
