# STEP-004 — 2026-10-25 — desktop frontend dependency repair

Files: native-frg/apps/desktop-tauri/package-lock.json; .github/workflows/desktop-frontend.yml. Updated Vite 8.3.1 to 8.3.5 and associated resolved packages within existing manifest ranges; no application, consensus, network or mining behavior changed. Added Windows frontend CI (install without lifecycle scripts, audit, TypeScript and Vite build).

Completed implementation SHA: 8985bf4031cedf7651056f22026f4cbdf5fac59c. Parent handoff SHA: 517803bd7c2107afbd7ca8e1c85e1446e96323b5. This handoff follows the implementation commit.

Commands/results: npm ci --ignore-scripts --prefix native-frg/apps/desktop-tauri; npm run build --prefix ... passed initially with Vite 8.3.1. npm audit --json identified Vite advisory GHSA-587h-7wmj-h5pm and related advisories (one high-severity package). Confirmed published patched ranges at https://github.com/advisories/GHSA-587h-7wmj-h5pm. Ran npm update vite --ignore-scripts --prefix ...; npm run build passed with Vite 8.3.5 (18 modules); npm audit --audit-level=high reports zero vulnerabilities. Node v24.19.0, npm 11.17.0 on Windows. git diff --check passed.

Remote evidence: STEP-003's 26 offline tests passed at https://github.com/tgibbsz32/Forgecoin---Monero-FCMP-CARROT-Upgrade/actions/runs/40239781475 . New frontend CI pending at handoff creation.

Limits: npm audit is a known-advisory check, not a security audit. No Rust/Tauri installer build, sidecar staging, signing or runtime wallet/miner validation has passed. No old binary substituted. Native daemon/wallet compilation is still running in separate work/native-build and must be resolved in STEP-005; configuration skipped RPC functional tests due to missing Python modules. Local protected/scratch statuses remain unchanged.

Next: finish and record native compile result, fix reproducible build compatibility errors in isolation; then native consensus/fork mapping and FCMP++/CARROT integration remain the highest-priority implementation work. Official pool, observer, explorer integration, staging and packaging remain pending. No production launch or Solana implementation.
