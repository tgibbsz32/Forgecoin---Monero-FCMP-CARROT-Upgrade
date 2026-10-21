# ForgeCoin Governance Charter
**Version:** 0.1 — Provisional / Pre-Mainnet Draft  
**Status:** Design specification; not yet ratified or enforced on-chain  
**Project:** ForgeCoin (FRG) native proof-of-work network and wFRG Solana Token-2022 companion token  
**Last updated:** 2026-10-21

> **Notice:** This charter describes proposed governance and safeguards to be built and tested before production. Publication does not mean that elections have occurred, funds have been deposited, authorities transferred, or software deployed. The initial 25,000,000 wFRG limit is a **governance-amendable outstanding-supply ceiling**, not an immutable lifetime maximum. Monetary rules must ultimately be enforced in code, not merely stated here.

## 1. Mission and governing principles

ForgeCoin is designed around an independent Monero-derived RandomX proof-of-work blockchain, with a Solana Token-2022 companion asset (wFRG) whose issuance is authorized by eligible native FRG mining rewards. The governance chamber oversees Solana-side economics, treasury stewardship and community priorities; it **cannot force native FRG nodes to accept a consensus change**.

The governance system aims for:
1. **Earned issuance:** no founder premine or ICO allocation of wFRG; mining-linked issuance only under the active rules.
2. **Predictable monetary changes:** approved changes are disclosed in advance, prospective, auditable and time-delayed.
3. **Balanced representation:** token-weighted elections coexist with miner, developer, user and founder representation.
4. **Fair elections:** verifiable eligibility, publicly auditable counting, protections against duplicate votes and an appeals process.
5. **Privacy:** do not require public disclosure of a native FRG balance, legal name or personal documents as a routine condition of participation.
6. **Separation of powers:** treasury custody must not itself grant monetary-policy, mint, fee-configuration or confiscation authority.
7. **No retroactive reduction:** claims earned under an applicable block-height policy are accounted for at that historical policy.

## 2. Governance chamber composition

The chamber has **10 equal-vote seats**:

| Seat group | Seats | Selection |
| --- | ---: | --- |
| wFRG staking representatives | 5 | Elected through stake-weighted proportional multi-winner election |
| Native FRG miner representative | 1 | Elected by eligible, verified miner electorate |
| Developer representative | 1 | Elected by eligible, verified contributor electorate |
| Community/user representative | 1 | Elected by eligible, verified community electorate |
| Founder (original) | 1 | Founder-designated |
| Founder (constituency-side) | 1 | Founder-designated |
| **Total** | **10** | **One chamber vote per seat** |

Both founder seats are disclosed and equal to other individual seats; together they constitute 20% of chamber seats. A person holding two founder seats does not receive an additional casting vote or authority outside the published chamber procedures. A **5–5 tie fails**.

The founder participates in discussions for all groups; the two seats do not themselves confer the right to cast extra votes in constituent elections. Any later change to seat composition requires a constitutional amendment.

## 3. Initial representatives and first elections

### 3.1 Pre-election administration
Before a credible electoral base exists, the project may have provisional advisory representatives nominated through an open community process. Such representatives can help test rules, review proposals and publish recommendations, **but cannot ratify binding production monetary amendments on behalf of an unelected chamber**. Production asset permissions remain independently restricted.

The founder may coordinate initial administration and appoint the two disclosed founder seats. Interim security signers should be independent where feasible and operate under narrowly specified, auditable authority.

### 3.2 Election readiness and timing
- First formal readiness assessment: **90 days after public network launch**.
- Reassess every **30 days** if the criteria are not met.
- Indicative minimums: **100 verified unique community participants; 30 independently verified wFRG governance stakers; 10 independent native mining entities; 5 verified contributors; no verified beneficial owner controlling more than 40% of participating governance stake**.
- Day 180 is a public escalation/reporting milestone, **not an automatic authorization** to conduct an unrepresentative or captured binding election.
- If thresholds are unmet, provisional representation remains advisory and safeguarded authorities remain in place. Report reasons, participation data, and a new readiness review date.
- The first binding elections additionally require a defined voting algorithm, eligibility appeals, election software testing and independent review.

These numerical requirements are **provisional governance-design thresholds**, not established facts about network participation.

### 3.3 Terms
- Five stake-elected representatives: **six-month terms**.
- Miner, developer and community representatives: **12-month terms**.
- Founder seats: continuing under this draft, subject to the formal charter amendment process.
- Staggering, replacement elections, term-limit policies, recall petitions, vacancy handling and candidate nomination deadlines must be defined before the first binding election. A vacancy does **not** automatically lower the special monetary-approval thresholds.

## 4. Voter eligibility, identity and verification

### 4.1 General eligibility
Every on-chain voter demonstrates control of a registered governance wallet by signing an election-specific cryptographic challenge. Wallet control **does not establish one-person uniqueness**: one individual can control multiple addresses. Where elections are person-based, the same verified eligible person receives at most one vote per applicable electorate.

Require transparent registration deadlines, an auditable voter roll of pseudonymous eligibility credentials, an appeals channel and a snapshot of applicable voting power. Do not publish private verification evidence by default.

### 4.2 Supporting evidence
Possible evidence includes:
- **LinkedIn:** professional identity continuity and relevant experience, especially for representative candidates.
- **GitHub:** reviewed commits, code reviews, documentation, issue triage and other attributable contributions.
- **Social accounts:** account continuity and project participation on relevant channels.
- **ForgeCoin forum/community:** substantive participation over time, published work and moderation history.
- **Mining evidence:** independently verifiable block-production or pool-contribution proofs.
- **Privacy-preserving personhood credentials:** independently vetted proof of uniqueness without necessarily exposing identity publicly.

None of a LinkedIn account, X account, GitHub account, forum login or Solana address alone proves an individual is unique. Avoid equating public social popularity with voter eligibility. Manual-review eligibility decisions need reviewer separation, written criteria, appeals and reasonable accommodation for pseudonymous participants.

### 4.3 Constituency requirements
- **Staking electorate:** eligible wFRG governance stake continuously qualified for **30 days** before the published snapshot. Prevent double-counting from stake transfer, redelegation, borrowing and wallet splitting.
- **Miner electorate:** verified native FRG mining participation; include independent pool contributors if their contributions can be verified without duplicating a pool's own vote.
- **Developer electorate:** substantive reviewed development, documentation, testing or maintenance contributions within the previous **180 days**, assessed under published criteria.
- **Community electorate:** at least **60 days** of verifiable meaningful community participation, with privacy-aware uniqueness checks.

For constituency elections, default to **one verified eligible person/entity, one vote** as applicable; clearly define when a mining *entity* rather than an individual is entitled to vote. Publish and test the exact proportional multi-winner algorithm before staking-representative elections. Quadratic or square-root weighting alone does not prevent strategic wallet splitting.

### 4.4 Elections
1. Publish election timeline, seat eligibility, candidate disclosures, ballot methods and appeals process.
2. Open nominations and independently review challenges to candidate or voter eligibility.
3. Register governance wallets and apply privacy-preserving uniqueness screening where required.
4. Snapshot qualified stake and eligibility at the published cutoff.
5. Open a publicly auditable voting window; prevent duplicate use of the same stake or credential.
6. Count according to the previously published election algorithm; publish turnout and final result.
7. Provide a limited challenge/appeal window, then seat winners and publish authority and conflict disclosures.

## 5. Meetings, quorum and approval thresholds

**Chamber quorum:** at least **8 of 10 participating representatives** for ordinary decision meetings. Abstentions may count for attendance but never toward an affirmative tally. A tie fails.

| Decision | Minimum approval |
| --- | --- |
| Routine operational proposal | **6 affirmative chamber votes** |
| Ordinary development/treasury spending policy | **7 affirmative chamber votes** |
| Future issuance ratio or miner/staker allocation | **8 affirmative chamber votes plus stakeholder ratification** |
| Provisional supply-cap increase | **8 affirmative chamber votes plus stakeholder ratification** |
| Transfer-fee rate increase | **8 affirmative chamber votes plus stakeholder ratification** |
| Founder compensation increase | **7 affirmative votes among 8 non-founder members**, founders recused, **plus stakeholder ratification** |
| Ordinary emergency issuance suspension | **7 affirmative chamber votes**, or narrowly limited designated security pause pending ratification |

For protected economic changes, stakeholder ratification requires **15% of eligible staked voting power participating** and at least **two-thirds support among valid stake-weighted votes cast**. Voting power and denominators must be documented at the snapshot.

The charter should specify quorum rounding, treatment of abstentions and invalid ballots, and emergency reauthorization in machine-readable detail before binding implementation.

## 6. Economic policy at initial launch

### 6.1 Native FRG
ForgeCoin is an independent proof-of-work chain with a **120-second target block interval** and a proposed permanent **0.20 FRG-per-block tail emission**. Native block rewards are paid **100% to native miners** under native consensus. The native chain must continue operating if a Solana relayer or governance service is offline.

A fresh genesis candidate includes an approximately **11.92092895 FRG output to a deterministic no-known-private-key point**. It is an isolated candidate, not proof of immutable supply destruction nor a frozen public mainnet.

### 6.2 wFRG issuance
- Solana Token-2022 companion asset: **wFRG**, currently a *dual-issued companion*, not a redeemable 1:1 wrapped claim on native FRG.
- Initial token supply: **zero**. No founder ICO or wFRG premine.
- Eligibility begins at native **block 60**. Blocks 1–59 do **not** accrue retrospective wFRG claims.
- Gross issuance ratio: **0.5 wFRG for every 1 FRG of eligible, verified native block subsidy**.
- Each such wFRG issuance splits **90% to the eligible miner** and **10% to the staking rewards reserve**.
- Staking does **not** independently authorize newly minted tokens and carries **no guaranteed APY**. Rewards are derived from mining-authorized issuance.
- The applicable policy for each block is fixed by its effective activation height; newly approved ratios do not retroactively change previously earned claims.
- Governance and mint controllers must prevent duplicate claims, unauthorized minting, replay and incorrect treatment of chain reorganizations.
- Unpaid rewards and their verification state must be publicly accounted for. Native FRG addresses and private holdings need not be disclosed in governance records.

### 6.3 Provisional supply ceiling
**25,000,000 wFRG maximum outstanding supply** at launch, enforced by a program-controlled mint restriction. This is **not** a Token-2022 automatic hard-cap feature and not an immutable lifetime cap.

A change to this ceiling requires: a public proposal; supply forecasts and impact analysis; **at least 90 days' notice**; **8 of 10 chamber approvals**; qualified stakeholder ratification; and enforceable on-chain delayed execution. Under the ordinary protected process, cumulative cap increases are provisionally limited to **10% of the governing cap within any rolling 365-day period**. A larger increase must use a *separately defined constitutional-amendment procedure*; until such a procedure is ratified, it is **not authorized**.

The provisional cap and permanent FRG tail emission can conflict. Before public mining launch, implementation must clearly define the cap-exhaustion procedure. Preferred test policy: reject minting above cap, preserve separately verified earned claims in a public queue, and disclose that claims may remain unpaid indefinitely if no capacity or amendment is approved. Burns create headroom but do **not automatically authorize extra issuance outside eligible PoW rewards**. A production implementation cannot promise guaranteed payment if future governance rejects cap expansion.

### 6.4 Transfer-fee schedule

Initial fee: **1.00% / 100 basis points** of taxable wFRG transfer value. Governance-controlled maximum permitted rate: **2.00% / 200 basis points**, subject to enhanced approval for increases.

| Purpose | Basis points of transfer | Percent of transfer | Share of initial collected fee |
| --- | ---: | ---: | ---: |
| Burn reserve | 50 | 0.50% | 50% |
| Development/upgrade reserve | 20 | 0.20% | 20% |
| Protocol liquidity reserve | 20 | 0.20% | 20% |
| Founder compensation | 10 | 0.10% | 10% |
| **Total** | **100** | **1.00%** | **100%** |

Token-2022 TransferFee withheld amounts must be collected by an authorized controller. The extension **does not itself allocate four buckets, schedule burns or override its configured maximum fee per transaction**. That absolute fee maximum, and any possible fee exemptions or DEX incompatibilities, need explicit configuration/testing. Fee income depends on actual fee-bearing transfers.

- Review burn-reserve destruction every **30 days**, with a published, reserve-limited burn policy. No arbitrary burning of user-held balances.
- Founder compensation may not exceed **0.10% of taxable transfer value** without enhanced non-founder approval and stakeholder ratification; there is **no automatic authorized raise**.
- Reallocation among the burn, development, liquidity and founder buckets is a monetary-policy change and must use the protected process.
- Do not automatically re-mint every burned token, as doing so cancels the intended supply reduction.

### 6.5 Monetary-policy notice
For issuance-ratio changes, future reward allocations, supply cap increases, transfer-fee increases and founder compensation increases, require **at least 90 days' public advance notice before effectiveness**. Changes take effect prospectively, at a specified future native block height or Solana effective epoch as appropriate. A Solana fee update's protocol-specific epoch delay is **additional to**, not a substitute for, the charter's longer public notice.

## 7. Initial custody, powers and separation of authorities

The founder requests **initial control over funds obtained from transfer fees**. This charter accepts initial founder administration **of fee-derived treasury balances**, subject to segregation, published accounting, authorized purposes and legal/contractual restrictions. It does **not** grant the founder permission to redirect the burn reserve into personal spending or unilaterally increase the founder fee.

| Power / asset | Initial arrangement | Longer-term transition |
| --- | --- | --- |
| Mint wFRG | Restricted on-chain controller whose minting must correspond to verified eligible blocks; upgrades secured by independent security multisig | Timelocked chamber/stakeholder-governed controller |
| Change emission ratio / supply cap | Not available to a unilateral wallet; proposed settings are policy-bound | Enhanced chamber approval + stake ratification + delay |
| Update Token-2022 fee rate or its fee configuration | Separate authorized fee-configuration multisig/program with charter restrictions | Enhanced governance-controlled authority |
| Pause new wFRG issuance | Narrowly scoped emergency security authority with expiration and disclosure | Chamber-approved security process; never pauses native FRG mining |
| Collect fee proceeds | Authorized withheld-fee collector; founder-administered accounting/vault structure | Elected governance may approve migration |
| Spend development reserve | Founder administration for documented network purposes, subject to approved budget/purpose rules and disclosures | Governance-controlled or delegated treasury |
| Deploy liquidity reserve | Founder administration into approved liquidity arrangements, with transparent accounting | Governance-controlled liquidity treasury |
| Withdraw founder share | Founder-controlled designated compensation account only, at the approved rate | Any increase needs non-founder/holder approval |
| Burn reserve | Segregated vault subject only to the approved burn controller/policy | Governance-supervised burn policy |
| Alter custody or spend permissions | Not unilateral; approved, timelocked exact authority-change transactions | Enhanced chamber process with affected constituency consent when specified |

Production controls should segregate the four fee purposes on-chain and enforce permitted withdrawals, not merely use four spreadsheets or promises. The founder cannot self-grant mint authority through treasury custody.

Avoid granting wFRG a **Permanent Delegate** capable of seizing or burning arbitrary holder balances. Define separate upgrade authority, mint authority, freeze/pause authority if any, fee-config authority, withheld-fee withdraw authority, treasury spend authority and emergency pause authority. These are **different permissions**. A pause should target **new wFRG issuance**, not an unrestricted ability to freeze every user's tokens.

### 7.1 Changing authorities
The community may propose reallocating duties to elected officials. Changing who can mint, change fees, pause issuance, spend treasury funds or alter fee allocations requires a published permission-diff, named/new controller, precise transaction payload, risk analysis, enhanced **8/10** chamber approval, relevant stakeholder ratification and **90-day** execution delay. Transferring a fee bucket's custody should not bypass that bucket's purpose or the founder-compensation conflict rules. Never transfer unrestricted mint power directly to a single elected representative.

A production 3-of-5 security multisig is a **candidate arrangement**, not a confirmed signer roster or complete trust solution. Signers, recovery and emergency procedures need formal approval before deployment.

## 8. Proposal lifecycle and on-chain execution

1. **Submission:** Public forum post with proposal identifier, full text, category, proponent, exact changes, financial impact, conflict declarations and related source-code/transaction hashes.
2. **Discussion:** At least **14 days** of open review for ordinary proposals; at least **30 days** for monetary proposals. Monetary review occurs within, not instead of, the 90-day notice.
3. **Eligibility snapshot:** Publish voter-eligibility criteria, participation denominator, stake cutoff and permitted delegations; close conflicts and appeals per the election policy.
4. **Council ballot:** Seven-day recorded council voting window, using the class-specific quorum and approval threshold.
5. **Stakeholder ballot:** Ten-day recorded stakeholder window where required, subject to stake turnout, majority threshold, snapshot and anti-double-voting controls.
6. **Queue:** Approved *exact executable instructions* are placed into a timelock; the waiting period cannot be satisfied merely by a verbal promise.
7. **Execute:** Controller verifies approval proof, authority scope, block/epoch activation time, cap bounds, current state, nonces and expected changes. Execution fails closed if conditions changed.
8. **Audit:** Publish Solana signatures, native activation heights if applicable, balances, before/after parameter state and a status report.

Failed, expired, withdrawn or amended proposals require fresh approval of material changes. Emergency security actions must be narrowly bounded, independently logged, subject to rapid ratification and unable to create tokens or divert user balances.

Native FRG consensus changes require independent native release engineering and node adoption; they cannot be effected by a Solana governance instruction.

## 9. Conflicts of interest and accountability

All candidates and representatives declare relevant paid relationships, beneficial ownership where appropriate, control of affected contracts/treasuries, grants, relationships with bidding vendors, and direct financial interests in proposals. Conflicted members do not participate in approval of direct personal compensation or contracting decisions. Specifically, **both founder seats abstain** on increases to founder compensation; approval requires **7 of the remaining 8** and stakeholder ratification.

Publish anonymized eligibility decisions, election results, chamber attendance, votes, recusals, treasury receipts, payments, mint and burn accounting, security incidents and contract upgrades. Protect private identity evidence and native-chain transaction privacy.

Provide review/appeal procedures for voter or candidate disqualification, conflicts, misconduct and disputed election outcomes. Publish remedies for a representative who is ineligible, compromised, removed or unable to serve. A representative's public social prominence is not itself an exemption from screening.

## 10. Fiscal management and disclosures

Maintain auditable segregated ledgers for:
- Gross authorized wFRG by native block and active ratio.
- Miner allocation, claims paid, claims queued and failed claims.
- Staking allocation, accrued rewards and rewards distributed.
- Total minted and burned wFRG and current outstanding supply.
- Withheld transfer fees and actual amounts moved into the four destinations.
- Founder compensation, development invoices/grants, and liquidity assets and positions.
- Governance proposals, elections, policy version history and authorization changes.

A public dashboard should report eligible FRG emission, authorized wFRG emission, outstanding supply, burns, staking and unclaimed liabilities, treasury balances, trading/liquidity metrics and the comparative FRG/wFRG market rates **without presenting a guaranteed price peg**. Publication frequency: monthly initially, plus event-based disclosures for authority changes and emergencies.

## 11. Governance evolution

**Phase 0 — Disposable tests:** Prototype chamber election logic, registry, snapshot handling, mint claims, fee vaults, pausing, timelocks, and adverse scenarios. No production keys, real token value or production authority transfers.

**Phase 1 — Public launch under restrictions:** Fixed initial economics and safeguarded multisig/controller. Founder fee administration is disclosed and purpose-bound. Interim representatives advise but cannot bypass production protections.

**Phase 2 — Credible elected chamber:** Begin binding elections only after minimum participation, voter-verification and auditing standards are met. Representative terms and recall process commence.

**Phase 3 — Mature governance:** Timelocked, voter-approved controller updates; gradually transfer designated spending and policy authorities through explicit permission-by-permission votes. Explore privacy-preserving native FRG participation without forcing custody or public wallet disclosure.

**Phase 4 — Tail emission:** Review supply-ceiling headroom well before exhaustion; preserve proof-of-work-linked issuance if voters approve policy changes. No assumption of automatic inflation increases or arbitrage price parity.

## 12. Security and readiness requirements before production

The following are release blockers, not currently completed features:

- Independent testnet with **distinct network identity and genesis** from any production candidate.
- Mining validation across heights 59, **60**, 61 and the actual native difficulty-adjustment schedule.
- Versioned, strictly validated optional coinbase payout metadata for Solana addresses; privacy disclosure that a public address may link miner rewards.
- Oracle block-confirmation policy, reorg resilience, unique claim IDs, source-chain identity and anti-replay protection.
- Contract-enforced restricted minting, cap-checking, current-policy-by-height calculation, staking accounting and transparent queued liabilities.
- Token-2022 fee maximum, compatible liquidity routing and four-way segregation tested on Solana devnet.
- Burn controller, pause expiration, multisig membership, role handoff, authorization scopes and recovery testing.
- Election credential provider or process, privacy handling, independent audits, final tally algorithm, proxy/delegation rules and voter appeals.
- Governance program tests for vacancy, quorum, recusal, 5–5 tie, timelocks, fee increases and cap exhaustion.
- Economic simulation using the **actual native FRG reward schedule** and permanent tail emission; threat modeling, security review and clear risk disclosures.

## 13. Open constitutional questions and explicit non-final choices

To avoid treating an early discussion as an immutable commitment, these matters remain unresolved:

1. Precisely how the first elected nominees are chosen and provisional representatives nominated when a constituency is too small.
2. Definitive unique-person and miner-entity verification criteria, eligibility reviewers, cost, retention and appeals.
3. Exact proportional multi-winner election algorithm, delegation and representative recall/vacancy rules.
4. Governance voter quorum if staked supply is small or manipulated; ownership concentration measurement and snapshot custody rules.
5. Emergency pause maximum duration and conditions for independent review.
6. Initial multisig signers, key recovery, governance-program upgrade authority and founder's fee-vault technical custody model.
7. Absolute Token-2022 maximum fee per transaction; DEX handling of transfer fees; rules for exempt transactions.
8. Concrete constitutional amendment path for a supply increase beyond 10% in a rolling year.
9. How to resolve legitimately verified rewards blocked indefinitely by the provisional cap.
10. Whether quorum/threshold exceptions apply to unavoidable recusal or representative vacancy (no automatic exception is granted by this draft).
11. Whether any additional legal, taxation, consumer-protection or jurisdiction-specific disclosures are required.

## 14. Versioning and amendment history

- **v0.1 (2026-10-21):** Initial written governance design incorporating a ten-seat chamber (five wFRG stakers, miner, developer, community and two founder seats); provisional election gates; eligibility; special votes; a 25-million wFRG ceiling; 0.5:1 block-60 issuance; 90/10 miner-staker allocation; 1% fee and 2% maximum; separated fee treasuries with initial founder administration; 90-day monetary notice and time-delayed execution.

**Change-control rule:** Future revisions must distinguish (a) editorial clarifications, (b) approved binding economic amendments and (c) unratified proposals. A GitHub documentation edit alone does not grant on-chain legal or technical authority.
