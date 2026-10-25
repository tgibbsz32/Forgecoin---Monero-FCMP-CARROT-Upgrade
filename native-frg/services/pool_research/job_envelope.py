"""Offline, non-mineable Stratum job identity envelope.

This is NOT a mining job: it deliberately does not publish blob, target or nonce
and cannot validate shares. Native RandomX / nonce mapping remains unverified.
"""
from dataclasses import dataclass
from hashlib import sha256
from .template_adapter import Template, TemplateError

@dataclass(frozen=True)
class JobEnvelope:
    job_id: str
    height: int
    difficulty: int
    seed_hash: str
    template_fingerprint: str
    session_id: str

def build_job_envelope(template: Template, session_id: str) -> JobEnvelope:
    if not isinstance(template, Template):
        raise TemplateError("validated template required")
    if not isinstance(session_id, str) or not 1 <= len(session_id) <= 64 or not session_id.isascii():
        raise ValueError("invalid session id")
    if any(not (c.isalnum() or c in "-_") for c in session_id):
        raise ValueError("unsafe session id")
    if template.height < 1 or template.difficulty < 1:
        raise TemplateError("invalid work height or difficulty")
    if len(template.seed_hash) != 32:
        raise TemplateError("invalid seed")
    if template.reserve_size < 1 or template.reserved_offset + template.reserve_size > len(template.blocktemplate_blob):
        raise TemplateError("invalid reserved region")
    # Domain separation and length prefix prevent concatenation ambiguities.
    fields=(template.height.to_bytes(8,"big"),template.difficulty.to_bytes(32,"big"),
            template.seed_hash,template.blocktemplate_blob,template.blockhashing_blob,
            template.reserved_offset.to_bytes(8,"big"),template.reserve_size.to_bytes(2,"big"))
    transcript=b"ForgeCoin pool research job envelope v1\\0"
    for field in fields:
        transcript+=len(field).to_bytes(4,"big")+field
    fingerprint=sha256(transcript).hexdigest()
    job_id=sha256(b"ForgeCoin job-id v1\\0"+bytes.fromhex(fingerprint)+session_id.encode("ascii")).hexdigest()[:32]
    return JobEnvelope(job_id,template.height,template.difficulty,template.seed_hash.hex(),fingerprint,session_id)

def is_stale(job: JobEnvelope, current_height: int) -> bool:
    if not isinstance(job, JobEnvelope) or type(current_height) is not int or current_height < 1:
        raise ValueError("invalid job/height")
    return current_height != job.height
