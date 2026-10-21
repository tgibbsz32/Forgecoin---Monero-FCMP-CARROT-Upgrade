"""Immutable role snapshots and single-ballot practice elections, NOT binding governance."""
import sqlite3
import time
from services.governance_api import registry

CATEGORIES = {"miner", "developer", "community", "staking", "chamber"}
SCHEMA = """
CREATE TABLE IF NOT EXISTS practice_elections(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 category TEXT NOT NULL,
 title TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'open' CHECK(status IN ('open','closed')),
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS practice_electors(
 election_id INTEGER NOT NULL REFERENCES practice_elections(id),
 wallet TEXT NOT NULL,
 weight INTEGER NOT NULL CHECK(weight>0),
 PRIMARY KEY(election_id,wallet)
);
CREATE TABLE IF NOT EXISTS practice_ballots(
 election_id INTEGER NOT NULL,
 wallet TEXT NOT NULL,
 choice TEXT NOT NULL CHECK(choice IN ('yes','no','abstain')),
 submitted_at INTEGER NOT NULL,
 PRIMARY KEY(election_id,wallet),
 FOREIGN KEY(election_id,wallet) REFERENCES practice_electors(election_id,wallet)
);
"""

def connect():
    conn=registry.connect()
    conn.executescript(SCHEMA)
    return conn

def create(category,title,weights=None):
    """Local administrator ONLY. Weight input is provisional, NOT verified stake."""
    if category not in CATEGORIES or not (5<=len(title.strip())<=120):
        raise ValueError("Invalid category or title")
    if category=="staking" and weights is None:
        raise ValueError("Staking simulation requires explicit externally supplied weights")
    now=int(time.time())
    with connect() as conn:
        # Freeze qualifications at creation; later role changes do not silently alter this ballot.
        rows=conn.execute("""SELECT DISTINCT wallet FROM members ORDER BY wallet""").fetchall()
        voters=[w for (w,) in rows if category in registry.roles_for(w)]
        cur=conn.execute("INSERT INTO practice_elections(category,title,created_at) VALUES (?,?,?)",(category,title.strip(),now))
        eid=cur.lastrowid
        for wallet in voters:
            weight=weights.get(wallet,0) if category=="staking" else 1
            if type(weight) is not int or weight<0:
                raise ValueError("Invalid stake weight")
            if weight:
                conn.execute("INSERT INTO practice_electors(election_id,wallet,weight) VALUES (?,?,?)",(eid,wallet,weight))
    return eid

def cast(election_id,wallet,choice):
    if choice not in ("yes","no","abstain"):
        raise ValueError("Invalid practice ballot choice")
    with connect() as conn:
        election=conn.execute("SELECT status FROM practice_elections WHERE id=?",(election_id,)).fetchone()
        if not election or election[0]!="open":
            raise ValueError("Election missing or closed")
        if not conn.execute("SELECT 1 FROM practice_electors WHERE election_id=? AND wallet=?",(election_id,wallet)).fetchone():
            raise PermissionError("Not in this election's frozen eligible voter list")
        try:
            conn.execute("INSERT INTO practice_ballots(election_id,wallet,choice,submitted_at) VALUES (?,?,?,?)",
                         (election_id,wallet,choice,int(time.time())))
        except sqlite3.IntegrityError as exc:
            raise ValueError("Ballot already recorded for this voter and election") from exc
    return {"recorded":True,"binding":False}

def detail(election_id):
    with connect() as conn:
        row=conn.execute("SELECT category,title,status FROM practice_elections WHERE id=?",(election_id,)).fetchone()
        if not row: raise ValueError("Unknown practice election")
        total=conn.execute("SELECT COUNT(*),COALESCE(SUM(weight),0) FROM practice_electors WHERE election_id=?",(election_id,)).fetchone()
        cast_count=conn.execute("SELECT COUNT(*),COALESCE(SUM(e.weight),0) FROM practice_ballots b JOIN practice_electors e ON b.election_id=e.election_id AND b.wallet=e.wallet WHERE b.election_id=?",(election_id,)).fetchone()
    return {"category":row[0],"title":row[1],"status":row[2],"eligible_wallets":total[0],
            "eligible_weight":total[1],"ballots_cast":cast_count[0],"participating_weight":cast_count[1],"binding":False}

def close(election_id):
    with connect() as conn:
        result=conn.execute("UPDATE practice_elections SET status='closed' WHERE id=? AND status='open'",(election_id,))
        if result.rowcount!=1:raise ValueError("Election missing or already closed")
