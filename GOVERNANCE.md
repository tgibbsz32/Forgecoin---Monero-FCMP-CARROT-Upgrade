# ForgeCoin Governance

> **Monetary policy update (2026-10-24):** Proposed fresh mainnet now uses a **55,000,000 FRG primary-emission reference**, consisting of a **5,000,000 FRG disclosed genesis treasury** and an intended **50,000,000 FRG primary miner allocation**, while retaining perpetual **0.20 FRG/block tail emission**. **55M is NOT a hard cap**. The formula, new genesis, custody and tests remain pending; older 50M/no-premine statements are historical. See [monetary policy proposal](docs/MONETARY_POLICY_PROPOSAL_2026-10-24.md).

> **Owner policy update (2026-10-24):** Owner has requested design review of a **10-seat native FRG representative chamber**, without authorizing binding elections. Former wFRG staker seats are NOT converted into holder-weighted native FRG votes. Miner eligibility requires verifiable mining and enforceable native FRG bonding; implementation and seat allocation are unresolved. See docs/OWNER_POLICY_DECISIONS_2026-10-24.md.


> **Documentation status (2026-10-24):** This file describes consensus-change stewardship only. The provisional FRG governance charter is not ratified; native miner governance bonds, representative seats, quorum and binding elections are not implemented. Practice governance votes grant no authority. See governance-charter.md and docs/RELEASE_STATUS_2026-10-24.md.


ForgeCoin consensus is enforced by software run independently by node operators. Repository maintainers can propose and publish changes but cannot remotely force independent nodes to accept them.

## Ordinary changes

Documentation, interface, packaging, logging, performance, seed-list, and compatible RPC changes can ship in normal releases when they do not change block or transaction validity.

## Consensus changes

A proposal that changes rewards, supply, proof of work, difficulty, block timing, transaction validity, or privacy rules must include:

1. a public written specification and rationale;
2. implementation and tests;
3. security and economic impact analysis;
4. an activation height far enough in the future for review and upgrades;
5. release binaries and checksums before activation;
6. explicit communication to node operators, miners, pools, wallets, and exchanges.

Nodes adopt a consensus change only by running compatible software. If incompatible rules retain independent support, a chain split is possible.

## Emergency changes

Privately reported vulnerabilities may require limited disclosure before a fix is available. Maintainers should publish the technical explanation and affected versions after users have a reasonable opportunity to upgrade.

## Network health

The project should publish observed pool concentration and encourage miners to move before one operator approaches majority hash power. No identity-based pool cap is enforced because miners can divide one operation across multiple identities.
