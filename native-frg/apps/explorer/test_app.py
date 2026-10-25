"""Deterministic Flask/API regressions; no live daemon, wallet or network required."""
import io
import json
import unittest
from unittest.mock import patch

from apps.explorer import app as explorer

TXID = "d" * 64
HASH_A = "a" * 64
HASH_B = "b" * 64


def sample_header(height: int, block_hash: str = HASH_A) -> dict:
    return {
        "height": height, "hash": block_hash, "timestamp": 1800000000 + height * 120,
        "difficulty": 500000, "cumulative_difficulty": 500000 * (height + 1),
        "reward": 1192092895, "num_txes": 0, "block_size": 150,
        "major_version": 19, "prev_hash": HASH_A, "orphan_status": False
    }


class ExplorerRouteTests(unittest.TestCase):
    def setUp(self):
        explorer.cache.clear()
        explorer.app.config["TESTING"] = True
        self.client = explorer.app.test_client()
        self.tip_hash = HASH_A
        self.block_hash = HASH_A
        self.header_list_empty = False
        self.tx_json_valid = True
        self.rpc_calls = []

        def fake_node(method, params=None, direct=False):
            self.rpc_calls.append(method)
            if method == "get_info":
                return {
                    "height": 3, "target": 120, "difficulty": 500000,
                    "synchronized": True, "incoming_connections_count": 0,
                    "outgoing_connections_count": 1, "tx_pool_size": 0,
                    "top_block_hash": self.tip_hash,
                }
            if method == "get_block_headers_range":
                if self.header_list_empty:
                    return {"headers": []}
                return {"headers": [
                    sample_header(h, self.block_hash)
                    for h in range(params["start_height"], params["end_height"] + 1)
                ]}
            if method == "get_block":
                return {"block_header": sample_header(params.get("height", 1), self.block_hash),
                        "miner_tx_hash": HASH_A, "tx_hashes": [TXID]}
            if method == "get_transactions":
                return {"txs": [{
                    "in_pool": False, "block_height": 1, "confirmations": 2,
                    "block_timestamp": 1800000120, "pruned_as_hex": "abcd",
                    "as_json": (
                        '{"version":2, "vin":[], "vout":[], "rct_signatures":{}}'
                        if self.tx_json_valid else "invalid JSON"
                    )
                }]}
            raise AssertionError(f"Unexpected RPC method {method}")

        self.mock = patch.object(explorer, "node", side_effect=fake_node)
        self.mock.start()
        self.addCleanup(self.mock.stop)

    def test_genesis_and_nonempty_overview(self):
        response = self.client.get("/api/overview")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["height"], 3)
        self.assertEqual(data["tip_height"], 2)
        self.assertEqual(data["target_seconds"], 120)
        self.assertEqual(data["blocks"][0]["reward_atomic"], "1192092895")
        self.assertEqual(data["blocks"][0]["difficulty"], "500000")
        self.assertEqual(data["blocks"][0]["height"], 2)

    def test_empty_rpc_headers_returns_explicit_unavailable(self):
        self.header_list_empty = True
        r = self.client.get("/api/overview")
        self.assertEqual(r.status_code, 503)
        self.assertIn("unavailable", r.get_json()["error"])

    def test_read_only_no_generic_rpc_proxy(self):
        self.assertEqual(self.client.post("/api/overview").status_code, 405)
        self.assertEqual(self.client.post("/json_rpc", json={"method": "stop_daemon"}).status_code, 405)
        self.assertEqual(self.client.get("/api/missing").status_code, 404)
        self.assertEqual(self.rpc_calls, [])

    def test_reject_invalid_heights_without_rpc(self):
        for invalid in ("-1", "001", "9999999999", "javascript", "9a", "%3Cscript%3E"):
            with self.subTest(invalid=invalid):
                self.assertEqual(self.client.get("/api/block/" + invalid).status_code, 400)
        self.assertEqual(self.rpc_calls, [])

    def test_block_height_or_hash_and_confirmations(self):
        self.assertEqual(self.client.get("/api/block/1").status_code, 200)
        self.assertEqual(self.client.get("/api/block/" + TXID).status_code, 200)
        self.assertEqual(self.client.get("/api/block/3").status_code, 404)

    def test_block_list_pagination(self):
        result = self.client.get("/api/blocks?before=1")
        self.assertEqual(result.status_code, 200)
        self.assertEqual([x["height"] for x in result.get_json()["blocks"]], [1, 0])
        self.assertIsNone(result.get_json()["next_before"])

    def test_cache_does_not_reuse_results_after_tip_changes(self):
        first = self.client.get("/api/block/1").get_json()
        self.assertEqual(first["header"]["hash"], HASH_A)
        self.tip_hash = HASH_B
        self.block_hash = HASH_B
        # Simulate expiry of the brief network-info cache so a changed canonical
        # tip is detected; live requests naturally update after its TTL.
        explorer.cache.pop("info", None)
        second = self.client.get("/api/block/1").get_json()
        self.assertEqual(second["header"]["hash"], HASH_B)

    def test_transaction_rejects_malformed_rpc_json(self):
        self.tx_json_valid = False
        result = self.client.get("/api/tx/" + TXID)
        self.assertEqual(result.status_code, 503)

    def test_transaction_reports_actual_known_fields(self):
        result = self.client.get("/api/tx/" + TXID)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.get_json()["hash"], TXID)
        self.assertEqual(result.get_json()["size"], 2)
        self.assertEqual(result.get_json()["confirmations"], 2)

    def test_security_headers(self):
        response = self.client.get("/api/overview")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["Cache-Control"], "no-store")


class RpcPayloadTests(unittest.TestCase):
    def test_rpc_rejects_json_array_and_bad_result(self):
        for content in (b"[]", b"null", b'{"result":[]}', b'{"result":null}'):
            with self.subTest(content=content):
                with patch("apps.explorer.app.urllib.request.urlopen",
                           return_value=io.BytesIO(content)):
                    with self.assertRaises(explorer.Unavailable):
                        explorer.node("get_info")

    def test_rpc_converts_missing_block_to_missing_exception(self):
        with patch("apps.explorer.app.urllib.request.urlopen",
                   return_value=io.BytesIO(b'{"error":{"code":-2}}')):
            with self.assertRaises(explorer.Missing):
                explorer.node("get_block", {"height": 42})

    def test_headers_rejects_invalid_shape(self):
        with patch.object(explorer, "node", return_value={"headers": "wrong"}):
            with self.assertRaises(explorer.Unavailable):
                explorer.headers(0, 1)

    def test_negative_wide_value_unavailable(self):
        with self.assertRaises(explorer.Unavailable):
            explorer.wide({"wide_difficulty": "-1"}, "difficulty")
        with self.assertRaises(explorer.Unavailable):
            explorer.wide({"difficulty": -1}, "difficulty")


if __name__ == "__main__":
    unittest.main()
