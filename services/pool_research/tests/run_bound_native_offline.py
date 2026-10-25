"""Optional native RandomX -> bound-job offline integration regression.

Run from repository root:
 python -m services.pool_research.tests.run_bound_native_offline --executable PATH

Requires a separately compiled, trusted RandomX reference executable.
This test uses SYNTHETIC block data; no daemon, network, mining or payments.
"""
import argparse
from pathlib import Path
from services.pool_research.native_randomx_adapter import NativeRandomXAdapter
from services.pool_research.bound_job import BoundJobVerifier
from services.pool_research.template_adapter import validate_template

SEED = bytes.fromhex("2a91ebe3007fb301072c5b0c8e130c782d1218e4633f6a30e6c2d692b6ac5f05")
EXPECTED = "294083824fec5947ef2cd825e2bedcb34789e4cc6ad12d7823bcf0be51178f77"

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--executable",required=True,type=Path)
    args=p.parse_args()
    adapter=NativeRandomXAdapter(args.executable, timeout=45)
    actual=adapter(SEED,b"\x11"*76).hex()
    if actual!=EXPECTED:raise AssertionError("native RandomX reference mismatch")
    header=b"\x11\x11\xac\x02"+b"\x33"*32+b"\x00"*4
    hashing_blob=header+b"\x44"*32+b"\x01"
    block_blob=header+b"\x55"*48
    template=validate_template({"result":{
        "height":1,"difficulty":500000,"expected_reward":2384185222,
        "seed_hash":SEED.hex(),"blocktemplate_blob":block_blob.hex(),
        "blockhashing_blob":hashing_blob.hex(),"reserved_offset":len(block_blob)-8}})
    store=BoundJobVerifier()
    job=store.register(template,500000)
    result=store.inspect(job,"01020304",1,adapter)
    if result.status not in ("LOW_DIFFICULTY","POW_THRESHOLD_MET_UNCREDITED"):
        raise AssertionError("unexpected verification status")
    if result.status=="POW_THRESHOLD_MET_UNCREDITED" and not result.digest_hex:
        raise AssertionError("missing digest")
    print("PASS: native reference vector and offline bound-template threshold check")
    print("share_status:",result.status)
    print("NOTE: synthetic template, development RandomX executable; NEVER credited")

if __name__=="__main__":main()
