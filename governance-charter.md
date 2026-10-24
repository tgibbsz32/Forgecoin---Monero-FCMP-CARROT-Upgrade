# ForgeCoin Governance Charter

> **Owner policy update (2026-10-24):** **Owner decision (2026-10-24):** Revisit a **10-seat representative chamber** using native FRG only. This restores the *size* as a design target, **not** the old five wFRG staker-seat allocation or any founder entitlement. Exact seats, founder participation, voting thresholds, terms and veto rights require separate owner approval. Native FRG bonding remains technically unimplemented and all votes nonbinding. See docs/OWNER_POLICY_DECISIONS_2026-10-24.md.


> **Documentation status (2026-10-24):** Status clarification: this charter is a proposal, not binding governance. Mining-based FRG bond verification is not implemented; no seat allocation or quorum is ratified. The isolated candidate genesis output remains unproved permanently unspendable. See docs/RELEASE_STATUS_2026-10-24.md.

**Version:** 0.2 Ã¢â‚¬â€ Provisional / Pre-Mainnet Draft
**Status:** FRG-only working proposal; not ratified or enforced as binding governance
**Project:** ForgeCoin (FRG), an independent proof-of-work network
**Last updated:** 2026-10-22

> **Scope decision:** Launch and active development are **native FRG only**. No wFRG issuance, dual mining, mining-linked Solana rewards, Solana staking, transfer-fee token, companion mint, or Solana trading asset is authorized for V1. Previously proposed wFRG economics are withdrawn from the active design. Any future Solana representation requires a new design, independent security/economic review, and explicit approval. See [ROADMAP.md](ROADMAP.md).

## 1. Mission and principles

ForgeCoin aims to provide private, CPU-accessible peer-to-peer digital cash on its independent Monero-derived RandomX proof-of-work blockchain. The native network must function without Solana, token bridges, external relayers, custodians, or a central governance service.

1. **Native-first:** one launch asset (FRG), one consensus issuance schedule, and no additional token promises.
2. **Independent consensus:** native consensus changes require software releases and voluntary adoption by node operators; a committee cannot compel them.
3. **Balanced stewardship:** miners secure blocks but do not gain unilateral authority over project assets, development priorities or community governance.
4. **Fair participation:** representative selection must use reviewed, privacy-aware eligibility and duplication controls, not simply wallet balances.
5. **Transparent changes:** proposals, financial conflicts, source-code diffs, voting procedures and results are published before implementation.
6. **Privacy and security:** no ordinary participant should need to publicly disclose a native FRG balance or private identity documents.
7. **No implied mint rights:** no Solana-related mint or financial rights arise from holding, mining or contributing to FRG.

## 2. Native FRG economics

The current native chain targets **120 seconds per block** and proposes a permanent **0.20 FRG-per-block tail subsidy**. Native block subsidies are paid **100% to native miners** under native consensus. Mining pools may share native FRG under their disclosed payout methods; pool shares do not authorize additional assets or Solana claims.

The detailed emission formula, network configuration, activation heights and supply behavior must be validated against the actual native code. This charter does not establish an immutable cap and cannot override node consensus.

**There is no V1 wFRG mining ratio, block-height activation, staking-reserve allocation, companion supply ceiling, Token-2022 transfer-fee schedule, founder fee share, or bridge reserve.** The historical 0.5:1 and 90/10 arrangements are canceled proposals, not earnable entitlements.

## 3. Governance scope and representation

Governance concerns project-maintained software, shared project resources, published policies, grants, community participation and the proposal process. It cannot independently change the rules accepted by native full nodes.

The earlier proposed **10-seat chamber (including five wFRG staker-elected seats)** is **withdrawn as the active composition**. No replacement seat allocation, term schedule or binding chamber quorum is yet ratified. Native FRG miner representation will be **qualified by both independently verifiable mining activity and a native FRG governance bond**, rather than wFRG staking. That qualification does not grant miners unilateral control. The project must publish a revised representative model that prevents domination by miners, founders, concentrated holders, or infrastructure operators.

Potential constituencies to evaluate include verified community members, **qualified bonded native FRG miners** (including provable pool participants), developers, infrastructure operators and independent security contributors. These are candidates, not currently allocated seats or ballot rights. Provisional representatives may advise but must not claim binding authority.

### 3.1 Native FRG mining and governance bonds

**Design direction:** To acquire and retain *miner-constituency governance authority*, a miner representative must (a) demonstrate independently verified native FRG mining contribution, including legitimate pool participants, and (b) maintain a qualifying **native FRG bond** for the duration of the representative's term. FRG bonding is a governance-eligibility condition, **not proof-of-stake consensus, block validation, a source of yield, or an additional issuance stream**.

- Define minimum bonded FRG amount, a qualification period (provisional research target: **30 continuous days**), and an unbonding/cooldown policy in an independently reviewed specification before binding elections. The amount is **not yet set**.
- The bond must be verifiably controlled and unspendable under a reviewed mechanism for the qualification term; holding FRG in an ordinary wallet or signing a balance statement is **not sufficient proof** of an enforceable lock. Native Monero-derived privacy and time-lock mechanics require explicit feasibility testing.
- Eligibility must check actual mining contribution **and** the bond; merely buying and locking FRG must not qualify a non-miner as a mining representative.
- Losing verified mining eligibility, withdrawing or spending the bond, or expiry of its enforceable lock **suspends miner-representative authority** pending independent review, with defined appeal, vacancy and replacement procedures. Previously cast valid ballots are not automatically rewritten.
- The miner constituency should retain a defined voice in network stewardship, but no mining pool, hash-power majority, wealthy bondholder or founder may unilaterally control community funds or project governance. One verifiably independent eligible miner entity should not gain multiple ballots by splitting wallets or pool worker accounts.
- Bonded FRG is not promised interest or minted rewards. The rules must address forced unbonding, loss of keys, network reorgs and pooled mining without requiring public disclosure of unrelated wallet activity.
- **Current implementation status:** Native FRG bond verification, safe enforcement, independent reviewer quorum and authority suspension are not built. All existing practice votes remain nonbinding.

## 4. Identity, participation and eligibility

Demonstrating control of a public wallet or signing a challenge proves wallet control only; it does not prove unique personhood, independence or mining activity.

A proposed election system should:
- Publish eligibility standards, registration deadlines, candidate requirements and appeals.
- Avoid publishing private FRG holdings, recovery phrases or raw identifying evidence.
- Verify mining contribution independently, including pool participants without double-counting, and establish ongoing native FRG bond eligibility for miner representatives.
- Verify developer work and substantive community participation.
- Use election-specific snapshots and auditable anti-duplicate controls.
- Define explicit conflict-of-interest rules, vacancies, recalls, independent reviewers and secure vote counting.

**Existing governance API election categories and practice ballot demonstrations are experimental legacy prototypes**, not a ratified chamber or active Solana staking system. The former `staking` category must not be represented as a launch privilege or used for binding decisions.

## 5. Proposals and decision rights

Until a replacement constitution is approved, binding representative votes, protected economic ratifications, chambers with special issuance powers, and stakeholder votes based on wFRG are **not operational or authorized**.

A future procedure must specify: who may propose; who may vote; quorum; thresholds; disclosure and review periods; eligible identity snapshots; recusal; challenge and appeal windows; exact implementation artifacts; and independent security review. Any treasury or code authority must remain explicitly limited and independently accountable. An administrator's access to project infrastructure does not grant an unrestricted right to change native monetary policy.

For native consensus changes, relevant node operators and maintainers must independently assess and adopt releases. Governance approval alone never modifies consensus.

## 6. Treasury, funding and accountability

Any future project fund should have separately published sources of revenue, custody, permissions, expenses, audit records and conflict controls. **No Solana token transfer-fee treasury, staking reserve, or automatic founder compensation is authorized in V1.** Neither a founder nor a miner is entitled to extra native issuance by this charter.

Publish verifiable native-chain emission and mining statistics, software changes, security reports, community decisions and actual project expenses. Do not invent liquidity or exchange metrics.

## 7. V1 readiness and safeguards

Before public launch or binding governance, prioritize:
- Independent native FRG testnet/release validation, genesis and peer identity.
- Correct native mining, difficulty adjustment, tail rewards, pool compatibility and chain reorganizations.
- Wallet security, reliable transaction confirmation, peer discovery and backup/recovery.
- Independent node/miner participation and third-party security review.
- A privacy-aware, miner-independent governance proposal and membership process.
- Clear disclosure that neither governance eligibility nor native mining entitles participants to a Solana asset.

Do not deploy the practice governance API, local admin dashboard or mock Solana-category election flow as a production voter registry.

## 8. Future Solana interoperability (research only)

The future roadmap may explore a **redeemable, fully FRG-backed representation on Solana**, primarily for exchange access, payments and compatible DeFi use. This would be a separate optional project. It must not reuse the canceled mining-linked companion issuance as if it were a 1:1 backing mechanism.

Any proposed bridge requires native deposit verification, transparent reserve/liability accounting despite FRG privacy, independent controls, safe mint/burn and redemption, chain-reorganization handling, audits, legal review, credible liquidity and a decision to launch. Until those requirements are satisfied, **no wFRG token issuance or deployment is planned**.

See [ROADMAP.md](ROADMAP.md) for stage gates. Existing archived dual-mining materials are historical only and should not be used for mining pool, wallet or token implementation.

## 9. Open governance-design questions

1. Which representative groups and how many seats best balance bonded miner, user, contributor and infrastructure interests?
2. How are voter uniqueness, miner participation and community contribution verified without undue privacy intrusion?
3. What quorums, thresholds, terms and recall rules are fair for an independent FRG-only network?
4. Who independently oversees project-controlled funds and security-sensitive releases?
5. What native FRG bond amount, lock proof, duration, withdrawal procedure and enforcement method are feasible without compromising native privacy or ordinary PoW transfers?
6. Which governance features can remain off-chain and advisory until the network is mature?

## 10. Version history

- **v0.1 (2026-10-21):** Former proposed wFRG dual-issuance, staking, fee and stake-weighted chamber architecture; never ratified.
- **v0.2 (2026-10-22):** Explicit FRG-only project scope. Withdrew wFRG dual mining, companion issuance, staking economics and wFRG-dependent governance. Moved any Solana representation to optional future research; introduced a proposed native FRG governance bond requirement for miner representatives; native consensus unchanged.

**Change-control notice:** This document records a development planning decision. It does not prove that the native code changed, that a binding constitutional vote occurred, or that earlier prototype software has been removed.

## Development research artifact

See the [native FRG miner bond proposal and synthetic tests](research/governance_bonds/README.md). This isolated policy experiment verifies no real mining or lock proofs and grants no authority; production governance and native lock changes remain gated on independent review.
