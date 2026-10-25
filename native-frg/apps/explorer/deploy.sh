set -eu
cd /home/ubuntu/explorer
.venv/bin/pip install -r requirements.txt
.venv/bin/python smoke.py
sudo install -d /opt/forgecoin-explorer /home/ubuntu/explorer-backup
sudo cp -an /etc/nginx/sites-available/default /home/ubuntu/explorer-backup/nginx-default.original
sudo cp -a . /opt/forgecoin-explorer/
sudo chown -R root:root /opt/forgecoin-explorer
sudo chmod -R a+rX /opt/forgecoin-explorer
sudo install -m 644 forgecoin-explorer.service /etc/systemd/system/
sudo install -m 644 forgecoin-explorer-firewall.service /etc/systemd/system/
sudo install -m 644 nginx.conf /etc/nginx/sites-available/forgecoin-explorer
sudo ln -sfn /etc/nginx/sites-available/forgecoin-explorer /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl daemon-reload
sudo systemctl enable --now forgecoin-explorer.service forgecoin-explorer-firewall.service
sudo systemctl reload nginx
sleep 2
curl -fsS http://127.0.0.1/api/overview
