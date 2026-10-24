import unittest
from services.pool_research.randomx_validation import decode_seed,decode_hashing_blob,decode_digest
class RandomXValidationTests(unittest.TestCase):
    def test_expected_lengths(self):
        self.assertEqual(len(decode_seed("2a"*32)),32)
        self.assertEqual(len(decode_hashing_blob("11"*76)),76)
        self.assertEqual(len(decode_digest("29"*32)),32)
    def test_malformed_seed(self):
        for value in ("", "ab"*31, "ab"*33, "x"*64, 5, None):
            with self.subTest(value=repr(value)[:20]),self.assertRaises(ValueError):decode_seed(value)
    def test_malformed_blob(self):
        for value in ("", "a", "qq", "11"*262145, False, None):
            with self.subTest(value=str(value)[:20]),self.assertRaises(ValueError):decode_hashing_blob(value)
    def test_malformed_digest(self):
        for value in ("", "a"*63, "a"*65, "g"*64, [], None):
            with self.subTest(value=str(value)[:20]),self.assertRaises(ValueError):decode_digest(value)
if __name__=="__main__":unittest.main()
