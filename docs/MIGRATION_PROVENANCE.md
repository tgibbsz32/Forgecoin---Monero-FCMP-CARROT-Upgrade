# Native FRG migration provenance — 2026-10-25

Exclusive development destination: https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade

The unmodified source snapshot is staged at `native-frg/` from https://github.com/tgibbsz32/forgecoin commit `abd29371abf70dcebcddaf76c0788040f38871a6`. Its complete reachable Git ancestry is the second parent of migration commit `43e7f7a9d16f1705082877ba6ee7efa3604397a2`. The original destination commit `34392d39ee31ee227d72c1720483015739041ec1` is the first parent; its README is unchanged. Snapshot tree equality was checked before commit. No source files were rewritten or excluded.

Retain `native-frg/LICENSE`, `native-frg/NOTICE.md`, per-file copyright notices, and component licenses. This is source staging, not a binary distribution. Before packaging, inventory bundled dependencies and reproduce applicable notices and corresponding-source obligations, including XMRig GPLv3 if bundled. Historical documentation and deferred utility code are retained for attribution/history only; Solana/SPL, swaps and dark-pool implementation are out of scope until native launch.

Build and test from `native-frg/`. Inherited `.github/workflows` are nested and inactive; review each before enabling any at repository root. Do not run inherited deployment scripts against production. There was no tracked `.gitmodules` at the source ref; dependency completeness must be verified before claiming a reproducible native build.

PR #100 in the source repository is unmerged draft `dcdde2c7571e2180ab81e9a173ccd395df0dba3` (re-resolve full SHA before importing). Its checker is only source-presence evidence, not a cryptographic port. Genesis unspendability, fork-version mapping, native consensus and CARROT wallet verification remain release blockers. Pool research accounting is not a Stratum server or payout service.

Local work preservation: TEMP/forgecoin-launch-work-20261025 contains explorer app changes, untracked explorer/test_app.py and pool_research/test_model.py import fix. They will be copied and tested in a separate step, preserving originals. C:/msys64/home/tgibb/forgecoin was inspected with read-only status only: four modified consensus/wallet files plus untracked difficulty header and tests/forgecoin remain untouched.
