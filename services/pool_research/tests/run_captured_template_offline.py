"""Offline-only runner for a locally supplied get_block_template response.

Example:
 python -m services.pool_research.tests.run_captured_template_offline \
   --capture PATH_TO_PRIVATE_JSON --executable PATH_TO_RANDOMX_EXE

Capture must contain the original RPC JSON response with template blobs.
Do NOT commit private capture files or wallet metadata. No RPC, wallet, daemon
launch, block submission, network listener, or payout accounting occurs here.
"""
import argparse
import json
from pathlib import Path

from services.pool_research.template_adapter import validate_template
from services.pool_research.bound_job import BoundJobVerifier
from services.pool_research.native_randomx_adapter import NativeRandomXAdapter

def verify_capture(response, verifier):
    template=validate_template(response)
    pool=BoundJobVerifier()
    job_id=pool.register(template,template.difficulty)
    # This nonce is a deterministic test input only. It does not mine a block.
    result=pool.inspect(job_id,"00000000",template.height,verifier)
    if result.status not in ("LOW_DIFFICULTY","POW_THRESHOLD_MET_UNCREDITED"):
        raise AssertionError("unexpected offline verification result")
    return {
        "height":template.height,
        "difficulty":template.difficulty,
        "hashing_blob_size":len(template.blockhashing_blob),
        "nonce_offset":pool._jobs[job_id].nonce_offset,
        "status":result.status,
        "credited":False,
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--capture",type=Path,required=True)
    parser.add_argument("--executable",type=Path,required=True)
    args=parser.parse_args()
    if args.capture.stat().st_size>1024*1024:
        raise ValueError("capture too large")
    with args.capture.open("r",encoding="utf-8") as file:
        response=json.load(file)
    summary=verify_capture(response,NativeRandomXAdapter(args.executable,timeout=45))
    # Print metadata only; never print raw template, seed, wallet or hashes.
    print(json.dumps(summary,sort_keys=True))

if __name__=="__main__":
    main()
