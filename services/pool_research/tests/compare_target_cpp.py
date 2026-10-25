"""Compile a standalone C++ arithmetic oracle and compare with Python.

Run explicitly from repository root:
  python -m services.pool_research.tests.compare_target_cpp
Requires g++ and Boost headers. Does NOT link ForgeCoin check_hash/RandomX.
"""
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from services.pool_research.pow_target import MAX_DIFFICULTY, MAX_HASH, meets_difficulty

def main():
    compiler = shutil.which("g++")
    if not compiler:
        raise RuntimeError("g++ not found; no native comparison was performed")
    source = Path(__file__).with_name("target_reference.cpp")
    rng = random.Random(20261024)
    cases = []
    for d in (1, 2, 400000, 500000, (1<<64)-1, 1<<64, (1<<64)+1, MAX_DIFFICULTY):
        t = MAX_HASH // d
        for h in (0, max(0, t-1), t, min(MAX_HASH, t+1), MAX_HASH):
            cases.append((d, h.to_bytes(32, "little")))
    for _ in range(300):
        cases.append((rng.randint(1, MAX_DIFFICULTY), rng.randbytes(32)))
    with tempfile.TemporaryDirectory(prefix="frg-target-") as temp:
        binary = Path(temp) / ("target_reference.exe" if __import__("os").name == "nt" else "target_reference")
        subprocess.run([compiler, "-std=c++17", "-O2", str(source), "-o", str(binary)],
                       check=True, timeout=90)
        text = "".join(f"{d} {digest.hex()}\n" for d, digest in cases)
        result = subprocess.run([str(binary)], input=text, text=True, capture_output=True,
                                check=True, timeout=20)
    output = result.stdout.splitlines()
    if len(output) != len(cases):
        raise AssertionError(f"Expected {len(cases)} results; got {len(output)}")
    mismatches = [i for i, ((d, digest), actual) in enumerate(zip(cases, output))
                  if actual != ("PASS" if meets_difficulty(digest, d) else "FAIL")]
    if mismatches:
        raise AssertionError(f"{len(mismatches)} mismatches; first index {mismatches[0]}")
    print(f"PASS: {len(cases)} C++/Python comparisons; 0 mismatches (40 boundaries, 300 randomized)")
    print("Scope: standalone threshold oracle only; not linked ForgeCoin native check_hash")

if __name__ == "__main__":
    main()
