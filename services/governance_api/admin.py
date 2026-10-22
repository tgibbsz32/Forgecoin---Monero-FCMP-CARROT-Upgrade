"""Opt-in loopback administrator service. Never mount in the public API."""
import os
import secrets
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from services.governance_api import applications, elections

ASSETS = Path(__file__).with_name("admin_static")


class Review(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: Literal["approve", "reject"]
    reason: str = Field(min_length=8, max_length=500)


class Election(BaseModel):
    model_config = ConfigDict(extra="forbid")
    category: Literal["miner", "developer", "community", "staking", "chamber"]
    title: str = Field(min_length=5, max_length=120)
    weights: dict[str, StrictInt] | None = None


def create_app():
    # Fail closed unless deliberately started in development with a strong secret.
    if os.environ.get("FORGECOIN_ENV") != "development" or os.environ.get("FORGECOIN_ADMIN_ENABLED") != "1":
        raise RuntimeError("Administrator dashboard requires explicit development opt-in")
    token = os.environ.get("FORGECOIN_ADMIN_TOKEN", "")
    reviewer = os.environ.get("FORGECOIN_ADMIN_REVIEWER", "").strip()
    if len(token) < 43 or not token.isascii() or not reviewer or len(reviewer) > 128:
        raise RuntimeError("Set a random administrator token (at least 43 ASCII characters) and reviewer identity")
    app = FastAPI(title="ForgeCoin local practice administration", docs_url=None, redoc_url=None, openapi_url=None)
    origin = "http://127.0.0.1:8766"

    @app.middleware("http")
    async def boundary(request: Request, call_next):
        # Ignore forwarded headers; the launcher disables proxy-header trust too.
        if not request.client or request.client.host not in ("127.0.0.1", "::1"):
            response = JSONResponse({"detail": "Loopback clients only"}, status_code=403)
        elif request.headers.get("host") != "127.0.0.1:8766":
            response = JSONResponse({"detail": "Invalid administrator host"}, status_code=403)
        elif request.headers.get("origin") not in (None, origin) or request.headers.get("sec-fetch-site") not in (None, "same-origin", "none"):
            response = JSONResponse({"detail": "Cross-origin requests forbidden"}, status_code=403)
        elif request.url.path.startswith("/api/") and not secrets.compare_digest(request.headers.get("authorization", "").encode(), ("Bearer " + token).encode()):
            response = JSONResponse({"detail": "Administrator authentication required"}, status_code=401)
        elif request.method == "POST" and request.headers.get("content-type", "").split(";")[0] != "application/json":
            response = JSONResponse({"detail": "JSON required"}, status_code=415)
        else:
            # Bound all incoming bodies, including chunked requests.
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 65536:
                    break
            if len(body) > 65536:
                response = JSONResponse({"detail": "Request too large"}, status_code=413)
            else:
                request._body = bytes(body)
                response = await call_next(request)
        response.headers.update({
            "Cache-Control": "no-store",
            "Content-Security-Policy": "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "no-referrer",
            "X-Frame-Options": "DENY",
        })
        return response

    @app.get("/")
    def dashboard():
        return FileResponse(ASSETS / "index.html")

    @app.get("/admin.js")
    def javascript():
        return FileResponse(ASSETS / "admin.js", media_type="text/javascript")

    @app.get("/admin.css")
    def stylesheet():
        return FileResponse(ASSETS / "admin.css", media_type="text/css")

    @app.get("/api/applications")
    def pending():
        with applications.connection() as conn:
            rows = conn.execute("SELECT id,wallet,role,evidence_reference,statement,status FROM applications WHERE status='pending' ORDER BY id LIMIT 100").fetchall()
        return {"applications": [dict(zip(("id", "wallet", "role", "evidence_reference", "statement", "status"), row)) for row in rows], "reviewer": reviewer}

    @app.post("/api/applications/{application_id}/review")
    def review(application_id: int, payload: Review):
        try:
            return applications.review(application_id, payload.action, reviewer, payload.reason)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/elections")
    def overview():
        return {"elections": elections.list_elections(), "binding": False}

    @app.post("/api/elections", status_code=201)
    def create(payload: Election):
        if payload.weights is not None:
            if payload.category != "staking" or len(payload.weights) > 500 or any(not 0 <= w <= 10**12 for w in payload.weights.values()):
                raise HTTPException(422, "Only staking accepts weights; maximum 500 entries, each 0–1 trillion")
        try:
            return {"id": elections.create(payload.category, payload.title, payload.weights), "binding": False}
        except ValueError as exc:
            raise HTTPException(422, str(exc)) from exc

    @app.post("/api/elections/{election_id}/close")
    def close(election_id: int):
        try:
            elections.close(election_id)
            return {"id": election_id, "status": "closed", "binding": False}
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    @app.get("/api/elections/{election_id}/tally")
    def tally(election_id: int):
        try:
            return elections.tally(election_id)
        except ValueError as exc:
            raise HTTPException(409, str(exc)) from exc

    return app


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(create_app(), host="127.0.0.1", port=8766, proxy_headers=False)
