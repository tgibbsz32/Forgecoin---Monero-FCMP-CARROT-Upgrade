"""Local-only, minimal full-template fixture serialization.

Use ONLY with a response already obtained from an isolated loopback daemon.
Never send the resulting fixture to GitHub; block template may contain wallet
identifiers. Preserve only fields needed by the offline verifier, no address.
"""
import json
import os
from pathlib import Path
from .template_adapter import validate_template

_FIELDS=("height","difficulty","expected_reward","seed_hash",
         "blocktemplate_blob","blockhashing_blob","reserved_offset")

def persist_private_capture(response, destination):
    template=validate_template(response,8)
    result=response.get("result",response)
    minimal={key:result[key] for key in _FIELDS}
    if os.name == "nt":
        raise PermissionError("Windows private capture disabled until explicit NTFS ACL enforcement is implemented")
    path=Path(destination)
    if path.exists():
        raise FileExistsError("refusing to overwrite private template capture")
    if path.is_symlink():
        raise ValueError("symlink destination not allowed")
    path.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    encoded=json.dumps({"result":minimal},separators=(",",":")).encode("utf-8")
    if len(encoded)>1024*1024:
        raise ValueError("private capture exceeds size limit")
    descriptor=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    try:
        with os.fdopen(descriptor,"wb") as file:
            file.write(encoded)
            file.write(b"\n")
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    return {"height":template.height,"difficulty":template.difficulty,
            "hashing_blob_size":len(template.blockhashing_blob),
            "blocktemplate_size":len(template.blocktemplate_blob)}
