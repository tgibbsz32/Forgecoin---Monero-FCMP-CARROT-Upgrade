"""Explicit offline RandomX reference-vector check against a prebuilt library.

Run from repo root:
 python -m services.pool_research.tests.compare_randomx_reference --source-root PATH --library PATH
No daemon, network, Stratum share verification, or block submission.
"""
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

SEED="2a91ebe3007fb301072c5b0c8e130c782d1218e4633f6a30e6c2d692b6ac5f05"
BLOB="11"*76  # Synthetic bytes, NOT a candidate mining blob
EXPECTED="294083824fec5947ef2cd825e2bedcb34789e4cc6ad12d7823bcf0be51178f77"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source-root",required=True,type=Path)
    parser.add_argument("--library",required=True,type=Path)
    args=parser.parse_args()
    compiler=shutil.which("g++")
    if not compiler:raise RuntimeError("g++ required on PATH")
    include=args.source_root.resolve()/"external"/"randomx"/"src"
    library=args.library.resolve()
    if not (include/"randomx.h").is_file() or not library.is_file() or library.name!="librandomx.a":
        raise RuntimeError("explicit RandomX headers and prebuilt library required")
    source=Path(__file__).with_name("randomx_reference.cpp")
    with tempfile.TemporaryDirectory(prefix="frg-rx-ref-") as temp:
        binary=Path(temp)/("randomx_reference.exe" if os.name=="nt" else "randomx_reference")
        subprocess.run([compiler,"-std=c++17","-O2","-I",str(include),str(source),
                        str(library),"-o",str(binary)],check=True,timeout=90)
        def digest(blob):
            p=subprocess.run([str(binary),SEED,blob],text=True,capture_output=True,check=True,timeout=60)
            return p.stdout.strip()
        actual=digest(BLOB)
        if actual!=EXPECTED:raise AssertionError(f"RandomX vector mismatch: {actual}")
        changed=digest("12"+BLOB[2:])
        if changed==actual:raise AssertionError("input mutation did not change digest")
    print("PASS: native light-mode RandomX expected digest and input-mutation check")
    print("Scope: synthetic 76-byte input; development library, not validated block/share")

if __name__=="__main__":main()
