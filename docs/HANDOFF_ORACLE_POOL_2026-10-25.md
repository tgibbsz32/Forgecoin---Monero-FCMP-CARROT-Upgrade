# Oracle FRG pool continuation — 2026-10-25

## Current authorization and boundaries

The user authorizes Oracle VM setup, public website/pool preparation and public
testing, replacing the earlier blanket no-public-network restriction. They
explicitly prohibit initiating the new mainnet or premining coins. Do not start
mining, submit blocks, initialize a new chain, change genesis, or enable payouts.
Use synthetic work for initial verification; it creates no chain or coins.
The user identified the existing height-519 chain as the OLD network. They
authorize retiring it when prudent. Preserve a recoverable backup first. Do not
stop it merely because it is old; remove dependencies and preserve rollback first.
No main-branch merge is authorized. Continue review branches and draft PRs.
After EACH completed stage, append an evidence-backed handoff here and refresh
the user-facing copy in the current chat outputs directory.

## Stage 0 completed: access recovered and read-only VM inventory

- Repository: tgibbsz32/forgecoin.
- Checkout: C:\Users\tgibb\Documents\Codex\2026-10-25\referenced-chatgpt-conversation-this-is-an\work\forgecoin
- Branch: codex/mining-preflight-pe-validation; pushed HEAD 0c4be4cae29931d086d3ad2043491d9eb731edb7.
- Draft PR: https://github.com/tgibbsz32/forgecoin/pull/92 . Prior PR 91 was already merged before this session.
- Existing untracked build-disposable/ is native build output: never add binaries.
- Oracle SSH: ubuntu@150.136.209.227. Hostname foregcon-vnic; aarch64.
- Existing key: C:\Users\tgibb\.ssh\oracle_forgecoin.key . Never print, copy into deliverables, or commit key material.
- Use BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=12. Existing known-host verification succeeded.
- Oracle identity URL supplied by user is a sign-in endpoint, not the pool hostname.
- VM observed: 11 GiB RAM, approximately 10 GiB available; 45 GiB root disk, 39 GiB free; zero load. These are observations, not quota/capacity guarantees.
- Active services: forgecoin, forgecoin-explorer, nginx and explorer firewall units.
- Existing daemon: /home/ubuntu/blockchain/forgecoin/build/arm64-release/bin/forged,
  data /home/ubuntu/forgecoin-test-data. P2P public 19480; RPC 127.0.0.1:19481;
  ZMQ 127.0.0.1:19482. No change made.
- get_info: height 519, nettype mainnet, difficulty 500000, peers 0,
  synchronized false. Tip 484316a1ff2e221849be859130c8a88f1e8b6212f19947e442a1aca7b2cf31e5.
  User confirms this is the OLD network; mainnet flag alone does not identify the future launch network.
- mining_status: active false, speed 0, threads_count 0.
- Explorer: 127.0.0.1:19800; /opt/forgecoin-explorer and /home/ubuntu/explorer.
- nginx listens 80/443; proxies explorer; ACME root /var/www/html;
  existing TLS certificate /etc/letsencrypt/live/150.136.209.227/fullchain.pem.
- /home/ubuntu/forgecoin-mainnet-staging contains source/build/smoke and candidate
  service files. Do not run any of them. A file/directory name is not authorization.
- No server changes, process starts, mining, chain initialization or coins created.

## Earlier engineering evidence and remaining work

See DESKTOP_MINING_PREFLIGHT_2026-10-25.md for exact native artifact digests,
MinGW build provenance and nine system DLL imports. Sidecar staging is digest
pinned; Windows Cargo and development staging refuse unreviewed artifacts.
Four Rust tests and nineteen Python tests passed; two process-launching Rust
tests remained ignored. Nine evidence controls passed. The ignored mining test
requires an externally-enforced egress acknowledgement; that is NOT enforcement.

XMRig candidate supplied by user:
C:\Users\tgibb\Downloads\xmrig-6.26.0-windows-x64\xmrig.exe
SHA256 6fa80698d7268f6e88aa88c06fb27ee99e1bcee747c2e76911e6206a5b1aeeb3.
Read-only x64 PE inspection passed; imports list only Windows system DLLs.
Its sibling downloaded ZIP has SHA256
99fe357f055577123c395b323d585b4ede8a326210b75fc73a47b88cc919e524,
which differs from upstream's v6.26.0 windows-x64 ZIP checksum
bba8097cb37d9b458a1cb1137876b27cde6740d17fe4ccbc086ba07d87d9e147.
Its executable matches that ZIP's executable; official provenance remains unverified.
Do not launch its existing scripts/config or WinRing0 driver. No miner was run.
For a controlled build fetch pinned upstream SOURCE, not binaries. Upstream
donation is not disabled by config zero; source policy and OS isolation matter.
Sources: https://github.com/xmrig/xmrig/releases/tag/v6.26.0 and https://xmrig.com/docs/miner .

services/pool_research is experimental offline code, NOT a deployable pool.
There is no verified production Stratum listener/payout pipeline. Mock Pool
acknowledgement does not validate RandomX. A native offline reference harness
exists in services/pool_research/tests; synthetic verification is allowed and
must not be described as actual accepted chain blocks or credited rewards.

## Next stages

1. Inspect existing nginx/explorer configuration and stage a separate honest
   pool-readiness website without changing the node or exposing its RPC.
2. Verify and deploy static pages on Oracle with a reversible nginx change,
   preserving explorer and ACME. Clearly label pool/mining/payouts unavailable.
3. Build native synthetic-work verification and real listener/accounting guards.
   Keep daemon block submission and payout connections absent/disabled.
4. Retire the old network only after dependency review and verified backup.
5. New-mainnet launch and coin-producing tests require separate authorization.

## Stage 1 completed: native ARM64 synthetic-work verification

2026-10-25, Oracle work directory /home/ubuntu/pool-preparation/20261025-native.
Copied only the offline adapter/bound-job dependencies and native reference
source/harness; no daemon or wallet was copied or launched. Compiled with g++
-std=c++17 -O2 against the existing development RandomX header/static library.

- Existing library SHA256: 5826e9ff627150c8565b6b1a2f1696250b23306122e794bc6430a9ba8356f18a.
- Header SHA256: 3187bf9ce958da3c2333a5dbc281340e5008ddd8a5811356032427a1d6ba845d.
- Reference source SHA256: d82b7ec64a5617bf16e38239c1aa96b6c2b1b54859b1b786aafccbfe5cab3647.
- Built reference executable SHA256: 14d500e51085622e44d5b840d727d7964c25d76291b2d6fc5f5c513564322781.
- compare_randomx_reference: expected vector and input-mutation check passed.
- Extended run_bound_native_offline: known vector passed; real native digest
  met difficulty-one threshold as UNcredited work; fixed work failed the maximum
  difficulty threshold; duplicate, stale, malformed and unknown submissions
  rejected before hash callback. Existing difficulty-500000 case: LOW_DIFFICULTY.
- Local adapter/bound-job regressions: 13 tests passed.
- Post-check daemon mining_status remains active=false, speed=0, threads=0.

Reproduce from that VM work directory:

```sh
python3 -m services.pool_research.tests.compare_randomx_reference --source-root /home/ubuntu/blockchain/forgecoin --library /home/ubuntu/blockchain/forgecoin/build/arm64-release/external/randomx/librandomx.a
python3 -m services.pool_research.tests.run_bound_native_offline --executable ./randomx_reference
```

Scope: synthetic fixed work and existing development library, NOT an independent
source attestation, live Stratum/miner integration, new-mainnet compatibility,
accepted chain block, credited share, production throughput, or payout proof.
No nonce search, chain initialization, block submission, coin creation, new
service or public listening port. Existing chain and explorer remain unchanged.
Next: complete/evaluate static pool preparation page, then reversible /pool/
deployment preserving existing explorer routes, ACME and disabled mining.

## Stage 2 completed: Oracle preparation website published

Public URL: https://150.136.209.227/pool/ . This is a preparation/readiness
website, NOT a functioning mining pool or live hashrate/payout dashboard.
Source: apps/pool-site/ . Exact authentic logo preserved. No JavaScript, external
font/image requests, analytics, forms, wallet inputs, API polling or connect/mining
controls. Explicitly labels old network, new-mainnet non-launch, disabled mining,
block submission and payouts; planned 1% fee is not represented as active charging.

Independent design review: PASS. Desktop browser and overflow checks passed.
Exact mobile/tablet pixel screenshots were unavailable in the browser control
surface; responsive CSS reviewed. No different-provider evaluator was available;
review was performed by a separate agent on the inherited model. No such limits
are evidence of a failed functional test; mobile visual QA remains outstanding.

Deployment helper: apps/pool-site-deploy.sh, Oracle-only, root via sudo.
It admits only static file extensions, refuses symlinks, validates existing nginx,
backs up its configuration, adds /pool/ routes to both existing HTTP/HTTPS server
blocks, validates/reloads nginx and checks assets/explorer. It never starts or
configures a miner, node or wallet. Existing explorer/ACME routes are preserved.
The first attempt failed its immediate route check and restored the original
configuration automatically. Inspection showed correct files/permissions; the
second attempt added a bounded readiness wait for graceful nginx worker turnover
and succeeded. Old failed v1 release/backup are retained for audit; do not mistake
their existence for the active deployment.

- Active release: /opt/forgecoin-pool/releases/preparation-20261025-v2/pool/ .
- Backup: /var/backups/forgecoin-pool/preparation-20261025-v2/nginx.conf .
- Staged source: /home/ubuntu/pool-preparation/site-20261025-v1/ .
- HTML SHA256 b953328f993725fa8ae69372edf881d90a4121fa73c09487bf821432e829a8c7.
- CSS SHA256 8a8eb25a481793f6527566b13c697791f31917423df786dcd08a476ebb85fcca.
- Logo SHA256 fd4aede81c6b50e78449722ba584e7cd3e0b94d4186e1ed7fc46fa938aca5a25.
- External HTTPS page/CSS/logo: HTTP 200; downloaded public HTML hash matches source.
- External POST /pool/: 405; old explorer root: 200.
- nginx -t passed; forgecoin, forgecoin-explorer and nginx remain active.
- Both forgecoin-mainnet-staging and forgecoin-mainnet-explorer-staging inactive.
- Daemon mining_status: active false, speed 0, threads 0; listening ports unchanged.
- No new chain, genesis change, block submission, premine or payout occurred.

Rollback (via the already verified SSH connection):

```sh
sudo cp -a /var/backups/forgecoin-pool/preparation-20261025-v2/nginx.conf /etc/nginx/sites-available/forgecoin-explorer
sudo nginx -t && sudo systemctl reload nginx
```

This restores the earlier explorer-only routing; static files can remain inert.
The helper intentionally refuses an already installed /pool/ route; future
updates must inspect/replace only that root rather than rerun initial install.
Old chain retirement is authorized but deferred while the old explorer remains
useful. No old-chain deletion or backup is claimed; take a consistent backup
and handle explorer dependencies before retiring it.

## Resume after stage 2

The pool website is published and native synthetic-work checks now execute on
Oracle ARM64. There is still no deployed Stratum listener or production accounting
service. Next implement bounded synthetic Stratum integration with the native
verifier, unique worker/job assignment, difficulty/duplicate/stale checks and
durable share bookkeeping. Keep chain submission and wallet/payout integrations
absent/disabled; never connect it to the old node as the future mainnet. Validate
timeouts, overload, restart and per-worker isolation before any miner-facing beta.
Trusted XMRig source build remains needed for later controlled client integration;
do not use the unverified download scripts. Actual coin-producing tests and new
mainnet launch remain outside current authorization. Append the next stage result
here, refresh the user-facing outputs handoff and push the review branch.
