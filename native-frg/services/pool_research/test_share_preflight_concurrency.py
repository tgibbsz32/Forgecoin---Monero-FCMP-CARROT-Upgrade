import unittest
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from services.pool_research.share_preflight import SharePreflight, SharePreflightError

class AtomicPreflightTests(unittest.TestCase):
    def test_concurrent_same_nonce_reserves_exactly_once(self):
        gate=SharePreflight()
        gate.register("job1",1)
        count=24
        barrier=Barrier(count)
        def submit(_):
            barrier.wait()
            try:
                return gate.inspect("job1","AbCd1234",1)
            except SharePreflightError:
                return "REJECTED"
        with ThreadPoolExecutor(max_workers=count) as executor:
            results=list(executor.map(submit,range(count)))
        self.assertEqual(results.count("READY_FOR_POW"),1)
        self.assertEqual(results.count("REJECTED"),count-1)
        self.assertEqual(len(gate.seen),1)

    def test_concurrent_distinct_nonces_are_not_lost(self):
        gate=SharePreflight()
        gate.register("job1",1)
        count=48
        with ThreadPoolExecutor(max_workers=16) as executor:
            results=list(executor.map(lambda i:gate.inspect("job1",f"{i:08x}",1),range(count)))
        self.assertEqual(results.count("READY_FOR_POW"),count)
        self.assertEqual(len(gate.seen),count)

    def test_registration_race_is_single_winner(self):
        gate=SharePreflight()
        def register(_):
            try:
                gate.register("job1",1)
                return "REGISTERED"
            except SharePreflightError:
                return "REJECTED"
        with ThreadPoolExecutor(max_workers=16) as executor:
            results=list(executor.map(register,range(40)))
        self.assertEqual(results.count("REGISTERED"),1)
        self.assertEqual(len(gate.jobs),1)

if __name__=="__main__":unittest.main()
