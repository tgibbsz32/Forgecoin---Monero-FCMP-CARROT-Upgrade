"""Explicit Linux namespace-only client test. No chain, blocks, coins or payouts.

Must run unprivileged with no capabilities/no-new-privileges inside a network
namespace containing ONLY loopback. Fails before spawning XMRig otherwise.
"""
import argparse
import asyncio
import errno
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import socket
import subprocess
import tempfile
import time

from services.pool_research.persistent_randomx import PersistentRandomXAdapter
from services.pool_research.synthetic_journal import SyntheticJournal
from services.pool_research.synthetic_listener import SyntheticListener


def check_isolation():
    if os.geteuid() == 0 or {name for _, name in socket.if_nameindex()} != {"lo"}:
        raise RuntimeError("requires unprivileged loopback-only network namespace")
    status = dict(line.split(":", 1) for line in Path("/proc/self/status").read_text().splitlines() if ":" in line)
    if (any(int(status[name].strip(), 16) for name in ("CapEff", "CapPrm", "CapInh", "CapAmb"))
            or status["NoNewPrivs"].strip() != "1"):
        raise RuntimeError("capabilities must be dropped and no-new-privileges set")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            # connect() on UDP only checks routing; no datagram is sent.
            probe.connect(("198.51.100.1", 9))
        except OSError as error:
            if error.errno != errno.ENETUNREACH:
                raise
        else:
            raise RuntimeError("non-loopback route unexpectedly available")


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--xmrig", type=Path, required=True)
    parser.add_argument("--worker", type=Path, required=True)
    parser.add_argument("--xmrig-sha256", required=True)
    parser.add_argument("--worker-sha256", required=True)
    args = parser.parse_args()
    check_isolation()
    for path, expected in ((args.xmrig, args.xmrig_sha256), (args.worker, args.worker_sha256)):
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise RuntimeError("executable digest mismatch")
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    version = subprocess.run([str(args.xmrig.resolve()), "--version"],
                             capture_output=True, text=True, check=True, timeout=5)
    if "6.26.0" not in version.stdout:
        raise RuntimeError("unexpected client version")
    print("ISOLATION: unprivileged, no capabilities, no-new-privileges, only loopback/no external route", flush=True)
    with tempfile.TemporaryDirectory(prefix="xmrig-synthetic-", dir=Path.cwd()) as temp:
        root = Path(temp)
        journal = SyntheticJournal(root / "checks.sqlite", max_records=8)
        adapter = PersistentRandomXAdapter(args.worker, timeout=10)
        listener = SyntheticListener(adapter, journal, capacity=1, idle_timeout=30, job_ttl=90)
        miner = None
        passed = False
        started = time.monotonic()
        try:
            port = await listener.start()
            config = {
                "autosave": False, "background": False, "colors": False,
                "donate-level": 0, "donate-over-proxy": 0,
                "http": {"enabled": False}, "opencl": False, "cuda": False,
                "randomx": {"init": 1, "mode": "light", "numa": False,
                            "1gb-pages": False, "rdmsr": False, "wrmsr": False},
                "cpu": {"enabled": True, "rx": [-1], "huge-pages": False,
                        "asm": False, "yield": True, "memory-pool": False},
                "retries": 1, "retry-pause": 1, "print-time": 0,
                "pools": [{"algo": "rx/0", "url": f"127.0.0.1:{port}",
                           "user": "synthetic-only", "pass": "x",
                           "tls": False, "keepalive": False}],
            }
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config))
            with (root / "client.log").open("wb") as log:
                miner = subprocess.Popen([str(args.xmrig.resolve()), "--config", str(config_path)],
                    stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                    cwd=root, start_new_session=True)
                while time.monotonic() - started < 40:
                    if journal.count() > 0:
                        passed = True
                        break
                    if miner.poll() is not None:
                        break
                    await asyncio.sleep(0.1)
                if not passed:
                    # Local diagnostic only: synthetic credentials and loopback.
                    print((root / "client.log").read_text(errors="replace")[-12000:])
                    raise AssertionError("no native-verified synthetic client submission recorded")
        finally:
            if miner is not None:
                try:
                    os.killpg(miner.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    await asyncio.to_thread(miner.wait, timeout=3)
                except subprocess.TimeoutExpired:
                    os.killpg(miner.pid, signal.SIGKILL)
                    await asyncio.to_thread(miner.wait, timeout=3)
            await listener.close()
            adapter.close()
            count = journal.count()
            scope = journal.db.execute("SELECT DISTINCT synthetic,credited FROM checks").fetchall()
            journal.close()
        if not passed or scope != [(1, 0)]:
            raise AssertionError("synthetic evidence scope invalid")
        print(f"PASS: XMRig client submitted native-verified rx/0 synthetic work; records={count}; credited=0")
        print("PASS: client, listener and worker stopped; disposable evidence removed; no chain/block/payout calls")


if __name__ == "__main__":
    asyncio.run(main())
