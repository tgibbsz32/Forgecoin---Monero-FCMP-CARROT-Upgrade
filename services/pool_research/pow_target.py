"""Offline 256-bit proof-of-work threshold arithmetic, not share verification.

Native check_hash interprets the 32-byte digest as a little-endian integer
and checks digest * difficulty <= 2**256 - 1.
No RandomX calculation, Stratum target serialization, or share acceptance.
"""
MAX_HASH=(1<<256)-1
MAX_DIFFICULTY=(1<<128)-1

def target_for_difficulty(difficulty: int) -> int:
    if type(difficulty) is not int or not 1 <= difficulty <= MAX_DIFFICULTY:
        raise ValueError("difficulty outside uint128 positive range")
    return MAX_HASH // difficulty

def meets_difficulty(digest: bytes, difficulty: int) -> bool:
    target=target_for_difficulty(difficulty)
    if not isinstance(digest,bytes) or len(digest)!=32:
        raise ValueError("expected 32-byte digest")
    return int.from_bytes(digest,"little") <= target

def target_as_32_le_bytes(difficulty: int) -> bytes:
    return target_for_difficulty(difficulty).to_bytes(32,"little")
