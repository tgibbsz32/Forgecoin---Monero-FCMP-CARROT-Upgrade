# Isolated native fresh-mainnet mining recheck â€” 2026-10-23

Read-only production scope; newly cloned local LMDB for test mining, no Oracle/live dev chain access.

- Test source: archived `isolated-fresh-mainnet-smoke/data` cloned into separate `isolated-height16-recheck-20261023/data`. Preserved archived original.
- Native Windows candidate binary: archived `builds/consensus-candidate-win64/bin/forged.exe` (preexisting candidate, not a fresh compile).
- Runtime: `--offline`, loopback P2P `39580`, RPC `39581`, `--no-zmq`; six CPU mining threads. No fixed-difficulty bypass.
- START: RPC height **8**, next difficulty **500000**, tip `783797eb386fd65f0d069b434a7838ab55e3535d97b21cf851b713c30b6091e4`.
- Mining RPC result: `OK`.
- Accepted block: RPC height **9**, next difficulty **500000**, tip `645fd0e92e4529731da52d0571fd55d7a81e3c3787fad1fa347b135033221dad`.
- Accepted block: RPC height **10**, next difficulty **500000**, tip `67e75b730e3982a69b4929845681d0981400b42e6764edd7e35971645931907b`.
- FINAL: RPC height **10**, next difficulty **500000**; test reported `TEST_STOPPED` and exit **0**.

**Important limitations:** Bounded mining did **not** reach consensus height 16; no startup-to-progressive-LWMA acceptance was tested. No actual fork competition or ARM64 cross-check occurred. The test regenerated no production chain data and did not change source or consensus parameters. Genesis spendability is still unverified.

Test script and log copy retained in local archived workspace's `isolated-height16-recheck-20261023` directory. Do not mistake this report for a mainnet release approval.
## Continued bounded mining — 2026-10-23

A second local offline run resumed the preserved disposable candidate chain from **RPC height 10** using the existing archived Windows candidate daemon and six CPU mining threads. It used `127.0.0.1:39581` RPC, loopback P2P port `39580`, `--offline`, `--no-zmq`, and no fixed-difficulty override.

- Start: height **10**, next difficulty **500000**, hash `67e75b730e3982a69b4929845681d0981400b42e6764edd7e35971645931907b`.
- Mining command: `OK`.
- One accepted new block: height **11**, next difficulty **500000**, hash `ab6fc7301a8fd95ae557d9a86f4babed723497ad1e5e1d62671083fa882d2edf`.
- Final: height **11**, exit **0**, daemon stopped via script's `finally` block.

**Not passed:** chain height 16 transition, full-window LWMA, genuine divergent-branch reorg, ARM64 agreement. No production/network changes; local isolated database retained as checkpoint.

