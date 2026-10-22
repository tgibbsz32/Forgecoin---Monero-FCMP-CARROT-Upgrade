> **SUPERSEDED HISTORICAL CONCEPT (2026-10-22):** Dual mining, wFRG Solana issuance, staking, mint/fee settings and activation heights below are **not part of current ForgeCoin development or V1 launch**. This document is retained solely for research history. See [ROADMAP.md](ROADMAP.md) and [governance-charter.md](governance-charter.md). Do not deploy or advertise this architecture.

# **Forgecoin (FRG) Dual-Mining & Tokenomics Architecture**

# **Executive Summary**

This document outlines the economic and technical architecture linking the native Forgecoin (FRG) privacy network with its mirrored Token-2022 asset (wFRG) on the Solana blockchain. This system solves the liquidity and velocity isolation of privacy coins by bridging absolute, network-level anonymity with high-speed, programmable DeFi liquidity.

# **1\. Dual-Mining Architecture (The Oracle Bridge)**

Because Solana cannot natively verify memory-hard Proof-of-Work (RandomX) hashes on-chain without exceeding compute limits, the dual-mining system relies on an off-chain Oracle Relayer to achieve simultaneous rewards.

* **The Miner's Tag:** Miners append their public Solana base58 wallet address to the `tx_extra` payload (using hex tag `0x53`) of their mined blocks on the native FRG chain.  
* **The Oracle Relayer:** A lightweight bot polls the native Forgecoin blockchain. When a block is solved, the bot waits for 10-30 block confirmations (to prevent reorg vulnerabilities), extracts the Solana address from `tx_extra`, and signs a transaction to mint the mirrored Solana asset.  
* **Activation Threshold:** Dual-mining activates at **Block 1,000**. This warm-up period prevents initial instamining, ensures decentralized hash power distribution, and establishes network stability before cross-chain rewards begin.

# **2\. Tokenomics: Mirrored Emission & Deflation**

To align the infinite tail emission required by the privacy chain with the speculative scarcity required by Solana DeFi, Forgecoin utilizes a 1:1 Mirrored Emission model paired with a Token-2022 Transfer Fee.

| Layer | Native Forgecoin (FRG) | Wrapped Forgecoin (wFRG) |
| :---- | :---- | :---- |
| **Role** | Security Layer (Native Chain) | Velocity Layer (Solana Token-2022) |
| **Total Supply** | 50,000,000 FRG | Hard-capped at 50,000,000 Tokens |
| **Emission Model** | Decays over \~38.1 years | 1:1 Dual-Mint Ratio with native chain |
| **Tail Emission** | 0.20 FRG / block (permanent network security) | Recycled via continuous supply burn |
| **Transfer Fee** | None (standard network gas) | 1% fee on every transfer/swap |

## **Wrapped Token Fee Allocation**

* **0.5% Developer Treasury:** Extracted directly as protocol revenue to fund continuous development and liquidity provisioning.  
* **0.5% Permanent Burn:** Automatically removed from circulation on every transaction, driving permanent deflation.

## **The Recycling Cap Mechanism**

Because **0.5% of all volume is permanently burned**, the active circulating supply of the Solana token is constantly driven below the 50,000,000 hard cap. This creates a supply vacuum, allowing the Oracle bot to continue minting tokens indefinitely to match the native tail emission without ever breaching the total supply ceiling.

# **3\. Utilization & Market Strategy (The Hybrid Approach)**

The architecture is designed to capture value through algorithmic arbitrage and protocol-owned liquidity.

* **Asymmetric Arbitrage Engine:** By establishing a market for the native privacy coin (CEX/OTC) and the Solana token (Raydium/Meteora), price discrepancies naturally occur. Arbitrage bots are incentivized to buy the cheaper asset and sell the more expensive one, maintaining tight peg parity across venues.  
* **The Volume Tax:** Every trade executed by arbitrage bots, retail users, and miners on Solana triggers the **1% transfer fee**, generating continuous, automated protocol revenue independent of market direction or asset price.  
* **Liquidity Provision (LP):** The **0.5% routed to the Developer Treasury** is continuously paired with SOL and deposited back into decentralized exchanges as Protocol-Owned Liquidity. This double-dip strategy allows the protocol to earn the **1% volume tax** on all movements *and* the **\~0.25% swap fees** from the DEX pools simultaneously.

# **4\. Feasible Future Developments (Roadmap)**

* **Full-Chain Membership Proofs (FCMP++):** Upgrades the anonymity set from 16 to the entire blockchain history. **Benefit:** Renders statistical deanonymization and chain-analysis attacks computationally infeasible while optimizing proof sizes for faster node verification.  
* **Seraphis and Jamtis Protocols:** A next-generation transaction protocol restructuring how view keys operate. **Benefit:** Significantly improves the security and usability of multi-signature (multisig) wallets, light-wallet servers, and subaddresses.  
* **Decoy Selection Upgrades (OSPEAD):** A mathematical framework to optimize decoy outputs. **Benefit:** Counters sophisticated analysis firms by ensuring the algorithm picks decoy outputs that perfectly mimic the spending habits of real users, preventing timing or clustering heuristics.  
* **Native Atomic Swaps:** Trustless cross-chain exchange protocols built directly into the desktop wallet. **Benefit:** Bypasses centralized exchange delistings and KYC requirements, providing censorship-resistant liquidity and decentralized fiat off-ramps (e.g., swapping native FRG for BTC or ETH).  
* **Rust Node Migration:** Rebuilding the C++ daemon into a modular, memory-safe Rust architecture (similar to Cuprate). **Benefit:** Eliminates C++ memory vulnerability risks, modernizes the codebase to attract new developers, and simplifies native integrations with the Solana Token-2022 Oracle bot and other Web3 infrastructure.
