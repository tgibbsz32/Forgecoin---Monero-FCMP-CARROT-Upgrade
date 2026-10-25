"""Loopback-only synthetic Stratum integration. NO chain, rewards or payouts.

Fixed test nonces only; do not point a miner at this research listener. Each
connection gets independent synthetic work. There is deliberately no daemon,
wallet, block-submission or reward-ledger integration.
"""
import argparse
import asyncio
import hmac
import json
import secrets
import time
from pathlib import Path

from .bound_job import BoundJobVerifier
from .native_randomx_adapter import NativeRandomXAdapter
from .pow_boundary import VerificationError
from .share_preflight import SharePreflightError
from .stratum_protocol import MAX_FRAME_BYTES, ProtocolError, SessionTable
from .template_adapter import validate_template

SEED = bytes.fromhex("2a91ebe3007fb301072c5b0c8e130c782d1218e4633f6a30e6c2d692b6ac5f05")


class SyntheticListener:
    def __init__(self, verifier, *, capacity=4, difficulty=1, idle_timeout=10,
                 job_ttl=60, request_limit=32):
        if not callable(verifier):
            raise ValueError("native verifier required")
        if type(capacity) is not int or not 1 <= capacity <= 8:
            raise ValueError("capacity must be 1..8 for research")
        if type(difficulty) is not int or not 1 <= difficulty <= 0xffffffff:
            raise ValueError("invalid research difficulty")
        if not 0 < idle_timeout <= 30 or not 0 < job_ttl <= 120:
            raise ValueError("invalid timeout")
        if type(request_limit) is not int or not 1 <= request_limit <= 64:
            raise ValueError("invalid request limit")
        self.verifier = verifier
        self.sessions = SessionTable(capacity)
        self.difficulty = difficulty
        self.idle_timeout, self.job_ttl = idle_timeout, job_ttl
        self.request_limit = request_limit
        self.busy = False
        self.tasks = set()
        self.writers = set()
        self.server = None

    async def start(self):
        # No host option: public listeners are intentionally outside this stage.
        self.server = await asyncio.start_server(
            self.handle, "127.0.0.1", 0, limit=MAX_FRAME_BYTES)
        return self.server.sockets[0].getsockname()[1]

    async def close(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
        for writer in tuple(self.writers):
            writer.close()
        if self.tasks:
            # Do not abandon an in-flight native subprocess on disconnect.
            await asyncio.gather(*tuple(self.tasks), return_exceptions=True)

    async def send(self, writer, request_id, result=None, error=None):
        writer.write((json.dumps({"id": request_id, "jsonrpc": "2.0",
                                 "result": result, "error": error}) + "\n").encode())
        await asyncio.wait_for(writer.drain(), 3)

    async def handle(self, reader, writer):
        task = asyncio.current_task()
        self.tasks.add(task)
        self.writers.add(writer)
        connection = secrets.token_hex(16)
        try:
            try:
                self.sessions.open(connection)
            except ProtocolError:
                await self.send(writer, None, error={"code": -1, "message": "capacity reached"})
                return
            store = BoundJobVerifier()
            job = None
            created = 0
            for _ in range(self.request_limit):
                raw = await asyncio.wait_for(reader.readline(), self.idle_timeout)
                if not raw:
                    return
                if not raw.endswith(b"\n") or len(raw) > MAX_FRAME_BYTES:
                    raise ProtocolError("invalid frame length")
                request_id = None
                try:
                    request = self.sessions.inspect(connection, raw)
                    request_id = request["id"]
                    params = request["params"]
                    if request["method"] == "login":
                        # Random previous-hash bytes isolate each worker's work.
                        header = b"\x10\x10\x01" + secrets.token_bytes(32) + bytes(4)
                        blob = header + b"\x44" * 32 + b"\x01"
                        template = validate_template({"result": {
                            "height": 1, "difficulty": self.difficulty,
                            "expected_reward": 0, "seed_hash": SEED.hex(),
                            "blockhashing_blob": blob.hex(),
                            "blocktemplate_blob": (header + b"\x55" * 48).hex(),
                            "reserved_offset": len(header) + 40}})
                        job = store.register(template, self.difficulty)
                        created = time.monotonic()
                        await self.send(writer, request_id, {
                            "id": connection, "status": "SYNTHETIC_ONLY",
                            "job": {"job_id": job, "blob": blob.hex(),
                                    "seed_hash": SEED.hex(), "height": 1,
                                    "target": (0xffffffff // self.difficulty).to_bytes(4, "little").hex(),
                                    "algo": "rx/0"}})
                    elif request["method"] == "keepalived":
                        await self.send(writer, request_id, {"status": "KEEPALIVED"})
                    else:
                        if params["id"] != connection or params["job_id"] != job:
                            raise ProtocolError("submission belongs to another session or job")
                        if time.monotonic() - created > self.job_ttl:
                            raise ProtocolError("stale job")
                        if self.busy:
                            raise ProtocolError("verifier busy; retry with a new request id")
                        self.busy = True
                        computed = []

                        def verify(seed, blob):
                            digest = self.verifier(seed, blob)
                            computed.append(digest)
                            return digest

                        try:
                            result = await asyncio.to_thread(
                                store.inspect, job, params["nonce"], 1, verify)
                        finally:
                            self.busy = False
                        if not computed or not hmac.compare_digest(
                                computed[0].hex(), params["result"].lower()):
                            raise ProtocolError("claimed digest mismatch")
                        if result.status != "POW_THRESHOLD_MET_UNCREDITED":
                            raise ProtocolError("low difficulty")
                        await self.send(writer, request_id, {
                            "status": "POW_THRESHOLD_MET_UNCREDITED",
                            "synthetic": True, "credited": False})
                except (ProtocolError, VerificationError, SharePreflightError) as error:
                    await self.send(writer, request_id,
                                    error={"code": -1, "message": str(error)})
        except (OSError, ValueError, asyncio.TimeoutError):
            # Oversized/partial frames and idle clients are closed, never hashed.
            pass
        finally:
            self.sessions.close(connection)
            self.writers.discard(writer)
            writer.close()
            try:
                await asyncio.wait_for(writer.wait_closed(), 3)
            except (OSError, asyncio.TimeoutError):
                pass
            self.tasks.discard(task)


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    args = parser.parse_args()
    listener = SyntheticListener(NativeRandomXAdapter(args.executable, timeout=10))
    port = await listener.start()
    print(f"SYNTHETIC ONLY: 127.0.0.1:{port}; no credits, chain or payouts", flush=True)
    try:
        await asyncio.Event().wait()
    finally:
        await listener.close()


if __name__ == "__main__":
    asyncio.run(main())
