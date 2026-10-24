# ForgeCoin pool research: offline accounting model

This directory is a **test-only model**, not a functioning mining pool, Stratum server or payout service. It opens no sockets, cannot validate RandomX shares or block templates, cannot mine, does not access wallet RPC, and cannot pay miners. Never deploy or advertise it as a working pool.

The `WorkerRegistry` simulates a 100-active-connection limit by unique connection ID; it is not an HTTP/TCP server and does not enforce a limit on real sockets. `allocate_reward` demonstrates deterministic integer splitting, including a 1% operator fee, of an *assumed eligible* atomic-unit reward based on example share weights. It is not PPLNS, does not determine actual eligible rewards, confirm blocks, account for orphaned blocks, account for payout transaction costs, or provide audit-quality bookkeeping. No policy is implied on minimum payout, rounding, pool-fee basis or confirmation threshold beyond this example.

Run offline: `python -m unittest discover -s services/pool_research -p test_model.py -v`.

Before a public pool, implement and independently verify native FRG-compatible Stratum/RandomX template handling, difficulty-vetted shares, durable share accounting, a real connection limiter, reorg-aware reward eligibility, payout safety, rate limiting, ARM64 runtime performance and actual 100-worker load testing. Solo mining and independent pools must remain permissionless, and the official pool's intended 1% fee must be separately disclosed from transaction costs.
