"""Offline preflight only: never accepts a mining share as valid proof-of-work."""
from dataclasses import dataclass, field
import re

_NONCE=re.compile(r"^[0-9a-fA-F]{8}$")

class SharePreflightError(ValueError):
    pass

@dataclass
class SharePreflight:
    jobs: dict[str,int] = field(default_factory=dict)
    seen: set[tuple[str,str]] = field(default_factory=set)

    def register(self, job_id: str, height: int):
        if not isinstance(job_id,str) or not 1<=len(job_id)<=64 or not job_id.isascii() or not job_id.isalnum():
            raise SharePreflightError("invalid job id")
        if type(height) is not int or height<1:
            raise SharePreflightError("invalid height")
        if job_id in self.jobs:
            raise SharePreflightError("duplicate job id")
        self.jobs[job_id]=height

    def inspect(self, job_id: str, nonce_hex: str, current_height: int) -> str:
        if not isinstance(job_id,str) or job_id not in self.jobs:
            raise SharePreflightError("unknown job")
        if type(current_height) is not int or current_height<1:
            raise SharePreflightError("invalid height")
        if self.jobs[job_id]!=current_height:
            raise SharePreflightError("stale job")
        if not isinstance(nonce_hex,str) or _NONCE.fullmatch(nonce_hex) is None:
            raise SharePreflightError("nonce must be 4-byte hex")
        identity=(job_id,nonce_hex.lower())
        if identity in self.seen:
            raise SharePreflightError("duplicate nonce for job")
        self.seen.add(identity)
        return "READY_FOR_POW"
