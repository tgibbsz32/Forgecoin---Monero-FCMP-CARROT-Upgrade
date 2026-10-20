# ForgeCoin Explorer

Read-only Flask API and responsive standalone web interface for the Oracle-hosted ForgeCoin node. See ../HANDOFF.md for deployment status and network access blocker.

Deploy source to /home/ubuntu/explorer, create its .venv and install requirements.lock.txt. Run smoke.py against the loopback daemon. deploy.sh installs /opt/forgecoin-explorer, isolated systemd services and nginx routing. It expects existing passwordless sudo and is intended for this server; inspect before reusing elsewhere.

Node RPC stays on127.0.0.1:19481. Explorer backend binds127.0.0.1:19800. nginx serves public port80. A separate Oracle cloud ingress rule must permit80. No account login, wallet keys or private transaction decoding are provided.
