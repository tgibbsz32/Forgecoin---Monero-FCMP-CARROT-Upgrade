"""Offline validation of RandomX reference inputs and digest format.

No miner acceptance, daemon RPC, wallet or network interaction.
"""
import re

_HEX=re.compile(r"^[0-9a-fA-F]+$")

def decode_seed(seed_hex: str) -> bytes:
    if not isinstance(seed_hex,str) or len(seed_hex)!=64 or not _HEX.fullmatch(seed_hex):
        raise ValueError("RandomX seed must be exactly 32 hex bytes")
    return bytes.fromhex(seed_hex)

def decode_hashing_blob(blob_hex: str) -> bytes:
    if not isinstance(blob_hex,str) or len(blob_hex)==0 or len(blob_hex)%2 or len(blob_hex)>524288 or not _HEX.fullmatch(blob_hex):
        raise ValueError("invalid hashing blob hex")
    return bytes.fromhex(blob_hex)

def decode_digest(digest_hex: str) -> bytes:
    if not isinstance(digest_hex,str) or len(digest_hex)!=64 or not _HEX.fullmatch(digest_hex):
        raise ValueError("RandomX digest must be exactly 32 hex bytes")
    return bytes.fromhex(digest_hex)
