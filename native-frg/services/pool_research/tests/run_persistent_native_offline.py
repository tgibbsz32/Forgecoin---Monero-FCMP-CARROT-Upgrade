"""Fixed-vector/recycle/seed-switch checks; no nonce search or chain I/O."""
import argparse
from pathlib import Path
import subprocess
import time
from services.pool_research.native_randomx_adapter import NativeRandomXAdapter
from services.pool_research.persistent_randomx import PersistentRandomXAdapter
from services.pool_research.tests.run_bound_native_offline import SEED, EXPECTED


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--reference", type=Path, required=True)
    args = parser.parse_args()
    reference = NativeRandomXAdapter(args.reference, timeout=30)
    worker = PersistentRandomXAdapter(args.worker, timeout=30)
    started = time.monotonic()
    try:
        for _ in range(65):
            if worker(SEED, b"\x11"*76).hex() != EXPECTED:
                raise AssertionError("persistent known-vector mismatch")
        if worker.starts != 2:
            raise AssertionError("worker did not recycle at its request bound")
        for seed, blob in ((SEED, b"\x12"+b"\x11"*75),
                           (b"\x27"*32, b"\x11"*76),
                           (SEED, b"\x11"*76)):
            if worker(seed, blob) != reference(seed, blob):
                raise AssertionError("seed-switch or mutation mismatch")
    finally:
        worker.close()
    for data in (b"1 bad bad\n", b"2 "+SEED.hex().encode()+b" 11\n",
                 b"x"*524401+b"\n", b"1 "+SEED.hex().encode()+b" 11"):
        result = subprocess.run([str(args.worker.resolve())], input=data,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=5)
        if result.returncode != 2 or result.stdout:
            raise AssertionError("native worker accepted malformed/oversized input")
    print("PASS: 65 known-vector requests, bounded recycle, mutation/seed-switch reference comparison")
    print("PASS: malformed/tag/oversized/partial frames refused; worker closed")
    print(f"Synthetic diagnostic duration: {time.monotonic()-started:.3f}s; NOT pool throughput")


if __name__ == "__main__":
    main()
