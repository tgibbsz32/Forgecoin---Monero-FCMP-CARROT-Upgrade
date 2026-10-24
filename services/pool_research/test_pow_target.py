import unittest
from services.pool_research.pow_target import (
    MAX_HASH,MAX_DIFFICULTY,target_for_difficulty,meets_difficulty,target_as_32_le_bytes)

class TargetTests(unittest.TestCase):
    def test_boundaries(self):
        for difficulty in (1,2,500000,MAX_DIFFICULTY):
            with self.subTest(difficulty=difficulty):
                target=MAX_HASH//difficulty
                self.assertEqual(target_for_difficulty(difficulty),target)
                self.assertTrue(meets_difficulty(target.to_bytes(32,"little"),difficulty))
                if target<MAX_HASH:
                    self.assertFalse(meets_difficulty((target+1).to_bytes(32,"little"),difficulty))
                self.assertEqual(int.from_bytes(target_as_32_le_bytes(difficulty),"little"),target)

    def test_little_endian_digest(self):
        self.assertTrue(meets_difficulty(b"\x01"+b"\x00"*31,500000))
        self.assertFalse(meets_difficulty(b"\x00"*31+b"\x01",500000))

    def test_reject_invalid_values(self):
        for difficulty in (0,-1,True,1.0,MAX_DIFFICULTY+1):
            with self.subTest(difficulty=difficulty),self.assertRaises(ValueError):
                target_for_difficulty(difficulty)
        for digest in (b"",b"\x00"*31,b"\x00"*33,"not bytes"):
            with self.subTest(length=len(digest)),self.assertRaises(ValueError):
                meets_difficulty(digest,500000)

if __name__=="__main__":unittest.main()
