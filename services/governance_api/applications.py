"""Application intake and reviewer-only decisions; local development prototype."""
import sqlite3
import time
from services.governance_api import registry

APPLICATION_ROLES = frozenset(("miner", "developer", "community"))
SCHEMA = """
CREATE TABLE IF NOT EXISTS applications (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 wallet TEXT NOT NULL REFERENCES members(wallet),
 role TEXT NOT NULL,
 evidence_reference TEXT NOT NULL,
 statement TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('pending','approved','rejected','withdrawn')),
 created_at INTEGER NOT NULL,
 updated_at INTEGER NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS one_pending_application ON applications(wallet,role) WHERE status='pending';
CREATE TABLE IF NOT EXISTS application_events (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 application_id INTEGER NOT NULL REFERENCES applications(id),
 action TEXT NOT NULL,
 actor TEXT NOT NULL,
 reason TEXT NOT NULL,
 created_at INTEGER NOT NULL
);
"""

def connection():
    conn=registry.connect()
    conn.executescript(SCHEMA)
    return conn

def submit(wallet, role, evidence_reference, statement):
    if role not in APPLICATION_ROLES:
        raise ValueError("role cannot be self-requested through application intake")
    if not (8 <= len(evidence_reference) <= 250 and evidence_reference.startswith(("https://", "ref:"))):
        raise ValueError("provide a safe external evidence reference, not raw identity documents")
    if not (10 <= len(statement.strip()) <= 500):
        raise ValueError("statement must contain 10–500 characters")
    now=int(time.time())
    with connection() as conn:
        conn.execute("INSERT OR IGNORE INTO members(wallet,created_at) VALUES (?,?)",(wallet,now))
        try:
            cur=conn.execute(
                "INSERT INTO applications(wallet,role,evidence_reference,statement,status,created_at,updated_at) VALUES (?,?,?,?,?,?,?)",
                (wallet,role,evidence_reference,statement.strip(),"pending",now,now))
        except sqlite3.IntegrityError as exc:
            raise ValueError("already pending for this category") from exc
        app_id=cur.lastrowid
        conn.execute("INSERT INTO application_events(application_id,action,actor,reason,created_at) VALUES (?,?,?,?,?)",
                     (app_id,"submit",wallet,"Applicant submitted eligibility request",now))
    return app_id

def mine(wallet):
    with connection() as conn:
        rows=conn.execute("SELECT id,role,status,created_at,updated_at FROM applications WHERE wallet=? ORDER BY id DESC",(wallet,)).fetchall()
    return [dict(zip(("id","role","status","created_at","updated_at"),r)) for r in rows]

def review(app_id, action, reviewer, reason):
    if action not in ("approve","reject") or not reviewer.strip() or len(reason.strip())<8:
        raise ValueError("review requires approved action, reviewer and substantive reason")
    now=int(time.time())
    with connection() as conn:
        row=conn.execute("SELECT wallet,role,status FROM applications WHERE id=?",(app_id,)).fetchone()
        if row is None or row[2]!="pending":
            raise ValueError("application missing or already decided")
        wallet,role,_=row
        if reviewer==wallet:
            raise ValueError("applicant cannot review their own application")
        conn.execute("UPDATE applications SET status=?,updated_at=? WHERE id=?",("approved" if action=="approve" else "rejected",now,app_id))
        conn.execute("INSERT INTO application_events(application_id,action,actor,reason,created_at) VALUES (?,?,?,?,?)",(app_id,action,reviewer,reason,now))
        if action=="approve":
            conn.execute("INSERT INTO role_decisions(wallet,role,action,reviewer,rationale,created_at) VALUES (?,?,?,?,?,?)",
                         (wallet,role,"approve",reviewer,"Application "+str(app_id)+": "+reason,now))
    return {"id":app_id,"status":"approved" if action=="approve" else "rejected"}

def audit(app_id):
    with connection() as conn:
        events=conn.execute("SELECT action,actor,reason,created_at FROM application_events WHERE application_id=? ORDER BY id",(app_id,)).fetchall()
    return [dict(zip(("action","actor","reason","created_at"),r)) for r in events]
