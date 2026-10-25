"""Explicit offline native RandomX subprocess adapter for research.

No runtime build, network access, share acceptance, or payout accounting.
The caller must supply a locally trusted executable that accepts positional
seed/blob hex arguments and emits exactly one lowercase 32-byte digest.
Do not use this as a production isolation/security boundary.
"""
from pathlib import Path
import re
import subprocess

_HEX_DIGEST = re.compile(r"[0-9a-f]{64}\n?\Z")

class NativeRandomXError(ValueError):
    pass

class NativeRandomXAdapter:
    def __init__(self, executable: str | Path, timeout: float = 30.0):
        path = Path(executable).resolve(strict=True)
        if not path.is_file():
            raise NativeRandomXError("expected regular executable file")
        if type(timeout) not in (int, float) or not 0 < timeout <= 60:
            raise NativeRandomXError("invalid timeout")
        self._executable = path
        self._timeout = timeout

    def __call__(self, seed: bytes, blob: bytes) -> bytes:
        if not isinstance(seed, bytes) or len(seed) != 32:
            raise NativeRandomXError("seed must be 32 bytes")
        if not isinstance(blob, bytes) or not 1 <= len(blob) <= 262144:
            raise NativeRandomXError("invalid hashing blob size")
        try:
            result = subprocess.run(
                [str(self._executable), seed.hex(), blob.hex()],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                timeout=self._timeout, check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise NativeRandomXError("native RandomX execution failed") from exc
        if result.returncode != 0 or len(result.stdout) > 65:
            raise NativeRandomXError("native RandomX returned an invalid result")
        try:
            output = result.stdout.decode("ascii")
        except UnicodeDecodeError as exc:
            raise NativeRandomXError("non-ASCII digest output") from exc
        if not _HEX_DIGEST.fullmatch(output):
            raise NativeRandomXError("malformed native digest output")
        return bytes.fromhex(output.strip())
