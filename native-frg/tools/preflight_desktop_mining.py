#!/usr/bin/env python3
"""Read-only prerequisites for isolated desktop Solo/Pool acceptance tests."""
import argparse
import hashlib
import struct
from pathlib import Path

def inspect(path, label):
    if path is None:
        return "BLOCKED " + label + ": not supplied"
    p = Path(path)
    try:
        with p.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            handle.seek(0)
            dos = handle.read(64)
            if len(dos) != 64 or dos[:2] != b"MZ":
                return "BLOCKED " + label + ": missing DOS header"
            offset = struct.unpack_from("<I", dos, 60)[0]
            if offset < 64 or offset + 24 > size:
                return "BLOCKED " + label + ": invalid PE offset"
            handle.seek(offset)
            header = handle.read(24)
            if header[:4] != b"PE\0\0":
                return "BLOCKED " + label + ": missing PE signature"
            machine, sections, _, _, _, optional_size, flags = struct.unpack("<HHIIIHH", header[4:])
            if machine != 0x8664 or not flags & 2 or flags & 0x2000:
                return "BLOCKED " + label + ": expected x64 executable (not DLL)"
            if not 1 <= sections <= 96 or optional_size < 112:
                return "BLOCKED " + label + ": invalid PE header sizes"
            table = offset + 24 + optional_size
            if table + sections * 40 > size:
                return "BLOCKED " + label + ": truncated PE headers"
            optional = handle.read(optional_size)
            if optional[:2] != b"\x0b\x02":
                return "BLOCKED " + label + ": expected PE32+"
            handle.seek(table)
            for _ in range(sections):
                section = handle.read(40)
                raw_size, raw_offset = struct.unpack_from("<II", section, 16)
                if raw_size and (raw_offset < table + sections * 40 or raw_offset + raw_size > size):
                    return "BLOCKED " + label + ": invalid section extent"
            handle.seek(0)
            h = hashlib.sha256()
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                h.update(chunk)
    except (OSError, struct.error):
        return "BLOCKED " + label + ": file missing, unreadable or changed during inspection"
    return "FOUND " + label + ": sha256=" + h.hexdigest() + " (structure only; provenance unverified)"


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
