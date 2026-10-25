#!/usr/bin/env python3
"""Conservative desktop V1 mining evidence completeness gate.

This checks the structure of independently collected evidence; it does not prove
the claims in that evidence. Never include credentials or private templates.
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = {
    "solo": ("desktop_start_stop", "block_found", "block_accepted", "reward_matured"),
    "pool": ("desktop_start_stop", "shares_accepted", "invalid_shares_rejected",
             "stale_shares_rejected", "reconnect", "telemetry", "reward_credited",
             "payout_matured"),
}
HEX64 = re.compile(r"^[a-fA-F0-9]{64}$")
HEX40 = re.compile(r"^[a-fA-F0-9]{40}$")
SECRET_KEYS = {"seed", "mnemonic", "password", "private_key", "spend_key",
               "view_key", "secret", "rpc_password", "template_blob", "token"}


def validate(payload):
    problems = []
    if not isinstance(payload, dict):
        return ["evidence must be a JSON object"]
    for k in ("source_commit", "desktop_sha256", "daemon_sha256", "windows_version",
              "xmrig_version", "network", "captured_at_utc"):
        if not isinstance(payload.get(k), str) or not payload[k].strip():
            problems.append("missing metadata: " + k)
    if not HEX40.fullmatch(str(payload.get("source_commit", ""))):
        problems.append("source_commit must be a 40-character hex SHA")
    for k in ("desktop_sha256", "daemon_sha256"):
        if not HEX64.fullmatch(str(payload.get(k, ""))):
            problems.append(k + " must be a 64-character hex SHA256")
    stamp = payload.get("captured_at_utc")
    if isinstance(stamp, str):
        try:
            if not stamp.endswith("Z"):
                raise ValueError("not UTC Z")
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            if parsed > datetime.now(timezone.utc):
                problems.append("captured_at_utc must not be in the future")
        except ValueError:
            problems.append("captured_at_utc must be ISO 8601 UTC")
    network = str(payload.get("network", "")).lower()
    if network and not any(term in network for term in ("isolated", "disposable", "test-only")):
        problems.append("network must identify isolated test infrastructure")
    def walk(obj, path="$"):
        if isinstance(obj, dict):
            for key, value in obj.items():
                if str(key).casefold() in SECRET_KEYS:
                    problems.append("prohibited secret field: " + path + "." + str(key))
                walk(value, path + "." + str(key))
        elif isinstance(obj, list):
            for idx, value in enumerate(obj):
                walk(value, path + "[" + str(idx) + "]")
    walk(payload)
    for mode, checks in REQUIRED.items():
        section = payload.get(mode)
        if not isinstance(section, dict):
            problems.append("missing mode: " + mode)
            continue
        for check in checks:
            entry = section.get(check)
            if not isinstance(entry, dict) or entry.get("status") != "passed":
                problems.append(mode + "." + check + " not passed")
            elif not isinstance(entry.get("evidence_ref"), str) or not entry["evidence_ref"].strip():
                problems.append(mode + "." + check + " missing evidence_ref")
    return problems


def self_test():
    meta = dict(source_commit="a"*40, desktop_sha256="b"*64, daemon_sha256="c"*64,
                windows_version="Windows 11", xmrig_version="6.x",
                network="disposable isolated", captured_at_utc="2026-10-24T00:00:00Z")
    valid = dict(meta)
    for mode, checks in REQUIRED.items():
        valid[mode] = {c: {"status": "passed", "evidence_ref": "isolated-test-log:" + c}
                       for c in checks}
    assert not validate(valid), validate(valid)
    invalid = json.loads(json.dumps(valid))
    invalid["pool"]["payout_matured"]["status"] = "pending"
    assert any("pool.payout_matured" in x for x in validate(invalid))
    invalid = json.loads(json.dumps(valid))
    invalid["solo"]["block_accepted"].pop("evidence_ref")
    assert any("solo.block_accepted" in x for x in validate(invalid))
    invalid = json.loads(json.dumps(valid))
    invalid["password"] = "dummy"
    assert any("prohibited secret" in x for x in validate(invalid))
    invalid = json.loads(json.dumps(valid))
    invalid["captured_at_utc"] = "invalid"
    assert any("ISO 8601" in x for x in validate(invalid))
    invalid = json.loads(json.dumps(valid))
    invalid["network"] = "public mainnet"
    assert any("isolated" in x for x in validate(invalid))
    assert validate({})
    print("PASS: 7 evidence validation controls")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence", nargs="?", type=Path)
    p.add_argument("--self-test", action="store_true")
    args = p.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.evidence is None:
        p.error("evidence JSON required unless --self-test")
    try:
        payload = json.loads(args.evidence.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print("BLOCKED: cannot read valid evidence: " + str(error))
        return 2
    failures = validate(payload)
    for failure in failures:
        print("BLOCKED: " + failure)
    if failures:
        return 1
    print("PASS: structural evidence complete; verify authenticity manually before release")
    return 0


if __name__ == "__main__":
    sys.exit(main())
