"""Isolated reorg runner cleanup regression tests; no daemon, network or wallet use."""
import importlib.util
import pathlib
import types
import unittest

MODULE_PATH = pathlib.Path(__file__).with_name("isolated_reorg.py")
spec = importlib.util.spec_from_file_location("forgecoin_isolated_reorg", MODULE_PATH)
reorg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reorg)


class CleanupTests(unittest.TestCase):
    def node(self, failure=None):
        n = reorg.Node.__new__(reorg.Node)
        calls = []
        proc = types.SimpleNamespace(
            poll=lambda: None,
            wait=lambda timeout: calls.append("wait"),
            terminate=lambda: calls.append("terminate"),
        )
        n.proc = proc
        n.streams = []
        def request(endpoint, body=None):
            calls.append(endpoint)
            if endpoint == "stop_mining" and failure:
                raise RuntimeError(failure)
        n.request = request
        return n, calls

    def test_already_stopped_miner_still_stops_daemon(self):
        n, calls = self.node("{'status': 'Mining never started', 'untrusted': False}")
        n.stop()
        self.assertEqual(calls, ["stop_mining", "stop_daemon", "wait"])

    def test_other_mining_stop_error_is_not_suppressed(self):
        n, calls = self.node("Unexpected RPC failure")
        with self.assertRaisesRegex(RuntimeError, "Unexpected RPC failure"):
            n.stop()
        self.assertEqual(calls, ["stop_mining", "terminate", "wait"])

    def test_running_miner_cleanup(self):
        n, calls = self.node()
        n.stop()
        self.assertEqual(calls, ["stop_mining", "stop_daemon", "wait"])

    def test_exited_daemon_no_rpc(self):
        n, calls = self.node()
        n.proc.poll = lambda: 0
        n.stop()
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
