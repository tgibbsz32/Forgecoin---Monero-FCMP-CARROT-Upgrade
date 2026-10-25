"""Offline differential test using ForgeCoin's compiled check_hash symbol.

Run from repository root with:
 python -m services.pool_research.tests.compare_linked_native --source-root PATH --library PATH
Requires compatible g++, Boost/Monero headers and prebuilt libcryptonote_basic.a.
Never rebuilds or modifies a live daemon or consensus source tree.
"""
import argparse
import random
import shutil
import subprocess
import tempfile
from pathlib import Path
from services.pool_research.pow_target import MAX_HASH, MAX_DIFFICULTY, meets_difficulty

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-root",required=True,type=Path)
    p.add_argument("--library",required=True,type=Path)
    args=p.parse_args()
    compiler=shutil.which("g++")
    if not compiler:raise RuntimeError("g++ must be available on PATH")
    root=args.source_root.resolve()
    library=args.library.resolve()
    if not (root/"src"/"cryptonote_basic"/"difficulty.h").is_file():
        raise RuntimeError("missing expected native source headers")
    if not library.is_file() or library.name!="libcryptonote_basic.a":
        raise RuntimeError("explicit built cryptonote_basic static library required")
    rng=random.Random(20261024)
    cases=[]
    for d in (1,2,400000,500000,(1<<64)-1,1<<64,(1<<64)+1,MAX_DIFFICULTY):
        target=MAX_HASH//d
        for value in (0,max(0,target-1),target,min(MAX_HASH,target+1),MAX_HASH):
            cases.append((d,value.to_bytes(32,"little")))
    for _ in range(300):
        cases.append((rng.randint(1,MAX_DIFFICULTY),rng.randbytes(32)))
    source=Path(__file__).with_name("linked_check_hash.cpp")
    with tempfile.TemporaryDirectory(prefix="frg-native-check-") as tmp:
        exe=Path(tmp)/("linked_check_hash.exe" if __import__("os").name=="nt" else "linked_check_hash")
        subprocess.run([compiler,"-std=c++17","-O2","-I",str(root/"src"),
                        "-I",str(root/"contrib"/"epee"/"include"),str(source),
                        str(library),"-o",str(exe)],check=True,timeout=90)
        payload="".join(f"{d} {digest.hex()}\n" for d,digest in cases)
        output=subprocess.run([str(exe)],input=payload,text=True,capture_output=True,
                              check=True,timeout=20).stdout.splitlines()
    if len(output)!=len(cases):raise AssertionError("native checker returned wrong result count")
    failures=[i for i,((d,h),result) in enumerate(zip(cases,output))
              if result!=("PASS" if meets_difficulty(h,d) else "FAIL")]
    if failures:raise AssertionError(f"{len(failures)} mismatches; first at {failures[0]}")
    print(f"PASS: {len(cases)}/340 linked native check_hash comparisons; zero mismatches")
    print("Scope: provided prebuilt library only; RandomX and fresh-mainnet candidate not verified")

if __name__=="__main__":main()
