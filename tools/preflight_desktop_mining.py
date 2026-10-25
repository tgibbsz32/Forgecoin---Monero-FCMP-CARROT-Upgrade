#!/usr/bin/env python3
"""Read-only prerequisites for isolated desktop Solo/Pool acceptance tests."""
import argparse
import hashlib
from pathlib import Path

def inspect(path, label):
    if path is None:
        return "BLOCKED " + label + ": not supplied"
    p = Path(path)
    if not p.is_file():
        return "BLOCKED " + label + ": file missing"
    if p.stat().st_size == 0:
        return "BLOCKED " + label + ": empty file"
    with p.open("rb") as handle:
        magic = handle.read(2)
    if magic != b"MZ":
        return "BLOCKED " + label + ": not a Windows PE executable"
    h = hashlib.sha256()
    with p.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return "FOUND " + label + ": sha256=" + h.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--desktop", type=Path)
    parser.add_argument("--daemon", type=Path)
    parser.add_argument("--wallet-rpc", type=Path)
    parser.add_argument("--xmrig", type=Path)
    args = parser.parse_args()
    states = [inspect(getattr(args, k.replace("-", "_")), k)
              for k in ("desktop", "daemon", "wallet-rpc", "xmrig")]
    for state in states:
        print(state)
    if any(state.startswith("BLOCKED") for state in states):
        print("NOT VALIDATED: do not run acceptance or approve desktop V1")
        return 1
    print("PREREQUISITES PRESENT ONLY: functional Solo/Pool tests still required")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
