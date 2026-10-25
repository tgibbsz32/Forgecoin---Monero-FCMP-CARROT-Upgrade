# ForgeCoin pool preparation website

Static HTML and CSS intended for the existing Oracle VM at `/pool/`. This is
a readiness page, not a pool server or live dashboard. It makes no API calls,
contains no analytics, and uses only local assets and system fonts.

Mining connections, block submission, and payouts are disabled. Publishing
this page must not launch the new mainnet or mine coins. The existing explorer
at `/` represents the old development network and is explicitly labelled.

The 1% operator fee is planned policy on eligible mining rewards, separate from
transaction fees. No fees are currently collected by this pool.

## Local preview

From this directory, run `python -m http.server 8080 --bind 127.0.0.1` and open
`http://127.0.0.1:8080/`. Stop the preview when finished. To verify the deployed
path locally, serve a parent directory with this folder mapped as `pool`.

Deploy `index.html`, `styles.css`, and `assets/forgecoin-logo.png` together beneath
`/pool/`. Preserve existing explorer routes and ACME challenges. Do not publish
this README as the homepage. No build, Node dependencies, scripts, wallet access,
miner, daemon, or backend are needed.

The logo is an exact copy of `docs/images/forgecoin-logo.png`; do not redraw it.
