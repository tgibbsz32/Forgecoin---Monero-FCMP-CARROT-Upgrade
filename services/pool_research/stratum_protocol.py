"""Offline Stratum-style request/session validator.

Protocol boundary ONLY: no sockets, node RPC, RandomX verification, share acceptance,
payout logic, or miner authentication. JSON messages are data, never commands.
"""
import json
from dataclasses import dataclass, field

MAX_FRAME_BYTES = 4096
MAX_WORKERS = 100
MAX_LOGIN_LENGTH = 256
ALLOWED_METHODS = frozenset({"login", "submit", "keepalived"})

class ProtocolError(ValueError):
    pass

def parse_request(data: bytes) -> dict:
    if not isinstance(data, bytes) or not data or len(data) > MAX_FRAME_BYTES:
        raise ProtocolError("invalid frame length")
    try:
        obj = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("invalid JSON") from exc
    if not isinstance(obj, dict):
        raise ProtocolError("request must be a JSON object")
    if set(obj) - {"id", "method", "params"}:
        raise ProtocolError("unrecognized request field")
    if obj.get("method") not in ALLOWED_METHODS:
        raise ProtocolError("unsupported method")
    if "id" not in obj or type(obj["id"]) not in (str, int) or len(str(obj["id"])) > 64:
        raise ProtocolError("invalid request id")
    params = obj.get("params")
    if not isinstance(params, dict):
        raise ProtocolError("params must be object")
    method = obj["method"]
    if method == "login":
        if set(params) - {"login", "pass", "agent", "rigid"}:
            raise ProtocolError("unsupported login field")
        login = params.get("login")
        if not isinstance(login, str) or not 1 <= len(login) <= MAX_LOGIN_LENGTH:
            raise ProtocolError("invalid login")
        for key in ("pass", "agent", "rigid"):
            if key in params and (not isinstance(params[key], str) or len(params[key]) > 256):
                raise ProtocolError("invalid optional login field")
    elif method == "submit":
        if set(params) != {"id", "job_id", "nonce", "result"}:
            raise ProtocolError("incomplete submit")
        for key, width in (("id",64),("job_id",64),("nonce",8),("result",64)):
            v = params[key]
            if not isinstance(v,str) or not v or len(v)>width:
                raise ProtocolError("invalid submission field")
        for key in ("nonce","result"):
            v=params[key]
            if len(v)!=dict(nonce=8,result=64)[key] or any(c not in "0123456789abcdefABCDEF" for c in v):
                raise ProtocolError("invalid hex submission")
    elif params:
        raise ProtocolError("keepalived accepts empty params")
    return obj

@dataclass
class Session:
    connection_id: str
    authenticated: bool = False
    login: str | None = None
    seen_requests: set = field(default_factory=set)

class SessionTable:
    """Local accounting: not a TCP or security boundary."""
    def __init__(self, limit=MAX_WORKERS):
        if type(limit) is not int or not 1<=limit<=MAX_WORKERS:
            raise ValueError("invalid limit")
        self.limit=limit
        self.sessions={}

    def open(self, connection_id: str) -> Session:
        if not isinstance(connection_id,str) or not connection_id:
            raise ProtocolError("invalid connection id")
        if connection_id in self.sessions:
            raise ProtocolError("duplicate connection")
        if len(self.sessions)>=self.limit:
            raise ProtocolError("capacity reached")
        session=Session(connection_id)
        self.sessions[connection_id]=session
        return session

    def close(self, connection_id):
        self.sessions.pop(connection_id,None)

    def inspect(self, connection_id, raw: bytes) -> dict:
        session=self.sessions.get(connection_id)
        if session is None:
            raise ProtocolError("unknown session")
        req=parse_request(raw)
        rid=(type(req["id"]).__name__,req["id"])
        if rid in session.seen_requests:
            raise ProtocolError("duplicate request id")
        # Do not mutate state until syntactic and session checks pass.
        if req["method"]!="login" and not session.authenticated:
            raise ProtocolError("login required")
        if req["method"]=="login":
            if session.authenticated:
                raise ProtocolError("already logged in")
            session.login=req["params"]["login"]
            session.authenticated=True
        session.seen_requests.add(rid)
        return req
