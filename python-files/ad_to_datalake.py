#!/usr/bin/env python3
import mysql.connector
import subprocess
import sys
import json

def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)

def fetch_ad_members(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"[ERROR] Command failed (exit {result.returncode}):\n{result.stderr.strip()}", file=sys.stderr)
        return []

    lines = [l.strip() for l in result.stdout.splitlines() if l.strip()]
    members = []
    for line in lines:
        parts = line.split()
        if len(parts) < 2:
            continue
        samid = parts[0]
        fullname = " ".join(parts[1:])
        members.append((samid, fullname))
    return members

def upsert_operators(db_cfg, upsert_sql, members):
    conn = mysql.connector.connect(
        host=db_cfg['hostDB'],
        user=db_cfg['usernameDB'],
        password=db_cfg['passwordDB'],
        database=db_cfg['databaseDB'],
    )
    try:
        with conn.cursor() as cur:
            cur.executemany(upsert_sql, members)
        conn.commit()
        print(f"[INFO] Successfully upserted {len(members)} operator(s).")
    finally:
        conn.close()

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} path/to/config.json", file=sys.stderr)
        sys.exit(1)

    cfg = load_config(sys.argv[1])
    cmd = cfg.get('cmd')
    upsert_sql = cfg.get('upsertSQL')

    if not cmd or not upsert_sql:
        print("[ERROR] 'cmd' and 'upsertSQL' must be defined in config.json", file=sys.stderr)
        sys.exit(1)

    members = fetch_ad_members(cmd)
    if not members:
        print("[WARN] No AD members found or query failed. Existing data left untouched.", file=sys.stderr)
        sys.exit(1)

    try:
        upsert_operators(cfg, upsert_sql, members)
    except mysql.connector.Error as e:
        print(f"[ERROR] Database error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
