# STEP-001 — 2026-10-25 — attributable source staging

Completed: inspected destination access (admin/push), actual refs/history and existing README before changes. Destination had one commit, not an empty repository. Inspected upstream main and draft PR #100, owner policy and pool/explorer plan. Read both local statuses without modifying either checkout.

Files: exact 2,462-file upstream snapshot under native-frg/; retained LICENSE/NOTICE/component notices and full source ancestry. Added docs/MIGRATION_PROVENANCE.md and this handoff. Root README preserved byte-for-byte.

Commands/results: git clone; git fetch upstream main; git ls-tree; git status --short; GitHub repository/PR inspection. Initial git subtree add hit Windows long-path errors; enabled repository-local core.longpaths, materialized the existing index with git checkout-index -f -a, then validated complete tree equality using git write-tree and git rev-parse TREE:native-frg. Created two-parent migration with git commit-tree; git diff --exit-code passed and status was clean. No daemon/miner/deployment executed.

Source: abd29371abf70dcebcddaf76c0788040f38871a6. Destination base: 34392d39ee31ee227d72c1720483015739041ec1. Completed source commit: 43e7f7a9d16f1705082877ba6ee7efa3604397a2. This handoff is committed separately so it can reference the exact completed work SHA; its own SHA is discoverable with git log -- docs/handoffs/STEP-001-2026-10-25-source-staging.md.

Blockers: FCMP++/CARROT unported; genesis unresolved; build/dependency and binary license audit pending; no operational pool/payout evidence. No consensus modifications or activation authorized by migration. All production actions remain gated by explicit owner authorization.

Next: recover and review only the three specified scratch changes, rerun isolated Flask/accounting tests and commit STEP-002. Then bring over the read-only PR #100 readiness guard and validate it before native integration work.
