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
