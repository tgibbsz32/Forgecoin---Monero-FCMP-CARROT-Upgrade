"""Socket integration tests; fake digest unless FORGE_SYNTHETIC_NATIVE is set.

Native mode hashes fixed test nonces; never runs a miner or submits a block.
"""
import asyncio
import json
import os
import threading
import tempfile
import time
from pathlib import Path
import unittest
from .native_randomx_adapter import NativeRandomXAdapter
from .synthetic_listener import SyntheticListener
from .synthetic_journal import SyntheticJournal
from .persistent_randomx import PersistentRandomXAdapter


class ListenerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        executable = os.environ.get("FORGE_SYNTHETIC_NATIVE")
        persistent = os.environ.get("FORGE_SYNTHETIC_PERSISTENT")
        self.native = (PersistentRandomXAdapter(persistent, timeout=10) if persistent else
                       NativeRandomXAdapter(executable, timeout=10) if executable else None)
        self.calls = 0
        def verifier(seed, blob):
            self.calls += 1
            return self.native(seed, blob) if self.native else b"\x42" * 32
        self.verifier = verifier
        self.temp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp.name) / "synthetic.sqlite"
        self.journal = SyntheticJournal(self.db_path)
        self.listener = SyntheticListener(verifier, self.journal)
        self.port = await self.listener.start()
        self.clients = []

    async def asyncTearDown(self):
        for _, writer in self.clients:
            writer.close()
        await self.listener.close()
        if isinstance(self.native, PersistentRandomXAdapter):
            self.native.close()
        self.journal.close()
        self.temp.cleanup()

    async def client(self):
        pair = await asyncio.open_connection("127.0.0.1", self.port)
        self.clients.append(pair)
        return pair

    async def request(self, pair, rid, method, params):
        reader, writer = pair
        writer.write((json.dumps({"id": rid, "method": method, "params": params}) + "\n").encode())
        await writer.drain()
        return json.loads(await asyncio.wait_for(reader.readline(), 20))

    async def login(self, pair):
        response = await self.request(pair, 1, "login", {"login": "synthetic-worker"})
        self.assertIsNone(response["error"])
        self.assertEqual(response["result"]["status"], "SYNTHETIC_ONLY")
        return response["result"]

    async def submission(self, login, nonce="01020304"):
        job = login["job"]
        blob = bytes.fromhex(job["blob"])
        patched = blob[:35] + bytes.fromhex(nonce) + blob[39:]
        digest = await asyncio.to_thread(self.native, bytes.fromhex(job["seed_hash"]), patched) if self.native else b"\x42" * 32
        return {"id": login["id"], "job_id": job["job_id"],
                "nonce": nonce, "result": digest.hex()}

    async def test_xmrig_capabilities_on_wire(self):
        compatible = await self.client()
        reader, writer = compatible
        writer.write((json.dumps({
            "id": 1, "jsonrpc": "2.0", "method": "login",
            "params": {"login": "synthetic-only", "algo": ["rx/wow", "rx/0"]}
        }) + "\n").encode())
        await writer.drain()
        accepted = json.loads(await asyncio.wait_for(reader.readline(), 2))
        self.assertIsNone(accepted["error"])
        self.assertEqual(accepted["result"]["job"]["algo"], "rx/0")

        incompatible = await self.client()
        reader, writer = incompatible
        writer.write((json.dumps({
            "id": 1, "jsonrpc": "2.0", "method": "login",
            "params": {"login": "synthetic-only", "algo": ["rx/wow"]}
        }) + "\n").encode())
        await writer.drain()
        rejected = json.loads(await asyncio.wait_for(reader.readline(), 2))
        self.assertIn("does not support rx/0", rejected["error"]["message"])
        self.assertEqual(await asyncio.wait_for(reader.readline(), 2), b"")
        self.assertEqual(self.journal.count(), 0)

    async def test_native_or_fake_digest_success_duplicate_and_mismatch(self):
        pair = await self.client()
        login = await self.login(pair)
        params = await self.submission(login)
        response = await self.request(pair, 2, "submit", params)
        self.assertEqual(response["result"]["status"], "POW_THRESHOLD_MET_UNCREDITED")
        self.assertFalse(response["result"]["credited"])
        self.assertTrue(response["result"]["recorded"])
        self.assertEqual(self.journal.count(), 1)
        self.assertEqual(self.calls, 1)
        duplicate = await self.request(pair, 3, "submit", params)
        self.assertIn("duplicate", duplicate["error"]["message"])
        self.assertEqual(self.calls, 1)
        bad = await self.submission(login, "05060708")
        bad["result"] = "00" * 32
        mismatch = await self.request(pair, 4, "submit", bad)
        self.assertIn("digest mismatch", mismatch["error"]["message"])

    async def test_cross_worker_job_and_session_rejected_before_hash(self):
        first, second = await self.client(), await self.client()
        a, b = await self.login(first), await self.login(second)
        self.assertNotEqual(a["job"]["blob"], b["job"]["blob"])
        self.assertNotEqual(a["job"]["job_id"], b["job"]["job_id"])
        params = await self.submission(a)
        for rid, session in ((2, a["id"]), (3, b["id"])):
            params["id"] = session
            response = await self.request(second, rid, "submit", params)
            self.assertIn("another session or job", response["error"]["message"])
        self.assertEqual(self.calls, 0)

    async def test_stale_and_malformed_rejected_before_hash(self):
        pair = await self.client()
        login = await self.login(pair)
        params = await self.submission(login)
        params["nonce"] = "invalid!"
        response = await self.request(pair, 2, "submit", params)
        self.assertIsNotNone(response["error"])
        self.listener.job_ttl = 0
        params["nonce"] = "01020304"
        response = await self.request(pair, 3, "submit", params)
        self.assertIn("stale", response["error"]["message"])
        self.assertEqual(self.calls, 0)

    async def test_low_difficulty_and_verifier_failure_never_succeed(self):
        self.listener.difficulty = 0xffffffff
        pair = await self.client()
        login = await self.login(pair)
        response = await self.request(pair, 2, "submit", await self.submission(login))
        self.assertIn("low difficulty", response["error"]["message"])
        def failing(seed, blob):
            raise ValueError("deliberate verifier outage")
        self.listener.verifier = failing
        response = await self.request(pair, 3, "submit", await self.submission(login, "05060708"))
        self.assertIn("verifier failure", response["error"]["message"])

    async def test_capacity_and_idle_cleanup(self):
        self.listener.sessions.limit = 1
        self.listener.idle_timeout = 0.05
        first = await self.client()
        await self.login(first)
        second = await self.client()
        response = json.loads(await asyncio.wait_for(second[0].readline(), 2))
        self.assertIn("capacity", response["error"]["message"])
        self.assertEqual(await asyncio.wait_for(first[0].readline(), 2), b"")
        third = await self.client()
        await self.login(third)

    async def test_oversized_frame_and_request_limit(self):
        pair = await self.client()
        pair[1].write(b"x" * 4097 + b"\n")
        await pair[1].drain()
        self.assertEqual(await asyncio.wait_for(pair[0].readline(), 2), b"")
        self.listener.request_limit = 2
        pair = await self.client()
        await self.login(pair)
        await self.request(pair, 2, "keepalived", {})
        self.assertEqual(await asyncio.wait_for(pair[0].readline(), 2), b"")
        self.assertEqual(self.calls, 0)

    async def test_login_required_and_duplicate_request(self):
        pair = await self.client()
        response = await self.request(pair, 1, "keepalived", {})
        self.assertIn("login required", response["error"]["message"])
        await self.login(pair)
        response = await self.request(pair, 1, "keepalived", {})
        self.assertIn("duplicate request", response["error"]["message"])
        self.assertEqual(self.calls, 0)

    async def test_busy_rejection_does_not_queue_or_consume_nonce(self):
        first, second = await self.client(), await self.client()
        a, b = await self.login(first), await self.login(second)
        a_params, b_params = await self.submission(a), await self.submission(b)
        entered, release = threading.Event(), threading.Event()
        original = self.listener.verifier
        def blocking(seed, blob):
            entered.set()
            if not release.wait(3):
                raise ValueError("test barrier timed out")
            return original(seed, blob)
        self.listener.verifier = blocking
        pending = asyncio.create_task(self.request(first, 2, "submit", a_params))
        try:
            self.assertTrue(await asyncio.to_thread(entered.wait, 2))
            busy = await self.request(second, 2, "submit", b_params)
            self.assertIn("verifier busy", busy["error"]["message"])
        finally:
            release.set()
        self.assertIsNone((await pending)["error"])
        self.listener.verifier = original
        response = await self.request(second, 3, "submit", b_params)
        self.assertIsNone(response["error"])

    async def test_restart_preserves_records_but_not_live_jobs(self):
        pair = await self.client()
        old = await self.login(pair)
        old_params = await self.submission(old)
        self.assertIsNone((await self.request(pair, 2, "submit", old_params))["error"])
        await self.listener.close()
        self.journal.close()
        self.journal = SyntheticJournal(self.db_path)
        self.listener = SyntheticListener(self.verifier, self.journal)
        self.port = await self.listener.start()
        self.assertEqual(self.journal.count(), 1)
        pair = await self.client()
        current = await self.login(pair)
        old_params["id"] = current["id"]
        rejected = await self.request(pair, 2, "submit", old_params)
        self.assertIsNotNone(rejected["error"])
        self.assertEqual(self.calls, 1)
        params = await self.submission(current)
        self.assertIsNone((await self.request(pair, 3, "submit", params))["error"])
        self.assertEqual(self.journal.count(), 2)

    async def test_storage_failure_and_capacity_never_report_success(self):
        pair = await self.client()
        login = await self.login(pair)
        self.journal.db.execute("PRAGMA query_only=ON")
        response = await self.request(pair, 2, "submit", await self.submission(login))
        self.assertIsNotNone(response["error"])
        self.assertIsNone(response["result"])
        self.assertEqual(self.journal.count(), 0)
        self.journal.db.execute("PRAGMA query_only=OFF")
        self.journal.max_records = 1
        response = await self.request(pair, 3, "submit", await self.submission(login, "05060708"))
        self.assertTrue(response["result"]["recorded"])
        response = await self.request(pair, 4, "submit", await self.submission(login, "090a0b0c"))
        self.assertIsNotNone(response["error"])
        self.assertEqual(self.journal.count(), 1)

    async def test_expiry_during_native_work_never_records(self):
        pair = await self.client()
        started = time.monotonic()
        login = await self.login(pair)
        params = await self.submission(login)
        original = self.listener.verifier
        def slow(seed, blob):
            time.sleep(0.06)
            return original(seed, blob)
        self.listener.verifier = slow
        # Client-side native digest calculation also takes time. Leave a small
        # margin at submission so expiry happens inside the server verifier.
        self.listener.job_ttl = time.monotonic() - started + 0.05
        response = await self.request(pair, 2, "submit", params)
        self.assertIn("stale job after verification", response["error"]["message"])
        self.assertEqual(self.journal.count(), 0)


if __name__ == "__main__":
    unittest.main()
