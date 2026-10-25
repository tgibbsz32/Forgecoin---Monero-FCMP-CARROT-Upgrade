#!/bin/sh
# Oracle-only static preparation-page deployment. No chain/miner/wallet actions.
# Run as root after transferring a reviewed static directory beneath
# /home/ubuntu/pool-preparation/site-*. Preserves explorer and ACME routes.
set -eu
[ "$(id -u)" = 0 ] || { echo 'Run via sudo' >&2; exit 1; }
source_dir=$(realpath "${1:?static source directory required}")
release=${2:?unique release name required}
case "$source_dir" in /home/ubuntu/pool-preparation/site-*) ;; *) exit 1 ;; esac
case "$release" in ''|*[!a-z0-9-]*) exit 1 ;; esac
config=/etc/nginx/sites-available/forgecoin-explorer
destination=/opt/forgecoin-pool/releases/$release
backup=/var/backups/forgecoin-pool/$release
[ -f "$source_dir/index.html" ] && [ -f "$source_dir/styles.css" ]
[ ! -e "$destination" ] && [ ! -e "$backup" ]
# Static files only: no symlinks or script/backend executables are published.
[ -z "$(find "$source_dir" -type l -print -quit)" ]
[ -z "$(find "$source_dir" -type f ! -name '*.html' ! -name '*.css' ! -name '*.png' ! -name '*.md' -print -quit)" ]
nginx -t
install -d -m 755 "$destination/pool" "$backup"
cp -a "$config" "$backup/nginx.conf"
cp -a "$source_dir/." "$destination/pool/"
chown -R root:root "$destination"
find "$destination" -type d -exec chmod 755 {} +
find "$destination" -type f -exec chmod 644 {} +
changed=no
rollback() {
    if [ "$changed" = yes ]; then
        cp -a "$backup/nginx.conf" "$config"
        nginx -t && systemctl reload nginx
    fi
}
trap 'rollback' EXIT
changed=yes
python3 - "$config" "$destination" <<'PY'
from pathlib import Path
import sys
config, release = map(Path, sys.argv[1:])
text = config.read_text()
anchor = "    location / {\n"
if text.count(anchor) != 2 or "location ^~ /pool/" in text:
    raise SystemExit("Unexpected nginx layout; review rather than overwrite")
route = f'''    location = /pool {{ return 301 /pool/; }}
    location ^~ /pool/ {{
        if ($request_method !~ ^(GET|HEAD)$) {{ return 405; }}
        root {release};
        index index.html;
        try_files $uri $uri/ =404;
        add_header X-Content-Type-Options nosniff always;
        add_header Content-Security-Policy "default-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; frame-ancestors 'none'; form-action 'none'" always;
        add_header Strict-Transport-Security "max-age=86400" always;
    }}
'''
config.write_text(text.replace(anchor, route + anchor))
PY
nginx -t
systemctl reload nginx
# A successful reload signal precedes replacement of old workers. A bounded
# readiness loop avoids interpreting an old worker's 404 as deployment failure.
attempt=0
until curl -fsS --max-time 3 http://127.0.0.1/pool/ | grep -q 'Preparing for launch'; do
    attempt=$((attempt + 1))
    [ "$attempt" -lt 20 ] || exit 1
    sleep 0.25
done
curl -fsS --max-time 10 -o /dev/null http://127.0.0.1/pool/styles.css
curl -fsS --max-time 10 -o /dev/null http://127.0.0.1/pool/assets/forgecoin-logo.png
curl -fsS --max-time 10 -o /dev/null http://127.0.0.1:19800/api/overview
changed=no
trap - EXIT
printf 'Static pool preparation site deployed. Backup: %s\nRelease: %s\n' "$backup" "$destination"
printf 'Rollback: sudo cp -a %s/nginx.conf %s && sudo nginx -t && sudo systemctl reload nginx\n' "$backup" "$config"
