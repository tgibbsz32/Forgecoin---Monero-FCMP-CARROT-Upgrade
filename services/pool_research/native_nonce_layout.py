"""Offline structural checks for ForgeCoin's serialized block hashing header.

Source reference: cryptonote_basic.h block_header serializer writes three
varints (major/minor/timestamp), 32-byte prev_id, then 4-byte nonce.
No RandomX, target calculation, share acceptance or network I/O.
"""
from .template_adapter import Template, TemplateError

def _varint(blob: bytes, start: int):
    value = 0
    for index in range(10):
        pos = start + index
        if pos >= len(blob):
            raise TemplateError("truncated header varint")
        byte = blob[pos]
        if index == 9 and byte > 1:
            raise TemplateError("header varint overflow")
        value |= (byte & 0x7f) << (7 * index)
        if not byte & 0x80:
            if index and value < (1 << (7 * index)):
                raise TemplateError("noncanonical header varint")
            return value, pos + 1
    raise TemplateError("header varint too long")

def nonce_offset(hashing_blob: bytes) -> int:
    if not isinstance(hashing_blob, bytes):
        raise TemplateError("hashing blob must be bytes")
    cursor = 0
    for _ in range(3):
        _, cursor = _varint(hashing_blob, cursor)
    offset = cursor + 32
    if offset + 4 > len(hashing_blob):
        raise TemplateError("truncated previous hash or nonce")
    return offset

def verify_header_nonce(template: Template) -> int:
    if not isinstance(template, Template):
        raise TemplateError("validated template required")
    offset = nonce_offset(template.blockhashing_blob)
    if template.blocktemplate_blob[:offset + 4] != template.blockhashing_blob[:offset + 4]:
        raise TemplateError("serialized headers do not match")
    return offset

def replace_nonce_in_hashing_blob(template: Template, nonce: int) -> bytes:
    if type(nonce) is not int or not 0 <= nonce <= 0xffffffff:
        raise ValueError("nonce must be uint32")
    offset = verify_header_nonce(template)
    blob = template.blockhashing_blob
    return blob[:offset] + nonce.to_bytes(4, "little") + blob[offset + 4:]
