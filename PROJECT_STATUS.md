# ForgeCoin Project Status

## October source recovery

The repository now includes the Tauri desktop 0.1.6, standalone read-only explorer,
and existing mainnet upgrades v17/500, v18/600 and v19/700. See
[SOURCE_RECOVERY.md](docs/SOURCE_RECOVERY.md) for provenance, exact rules and
validation limits. These are recovered implementations, not a newly tested release.
Historical Phase 3 component descriptions below refer to the Windows Forms app.

## Working components

- ForgeCoin mainnet identity and genesis block
- Version 16 consensus from height 1
- RandomX proof-of-work mining
- Eight-decimal FRG accounting
- Desktop node, wallet, address book, solo miner, pool-miner interface, and local explorer
- Local-only daemon and wallet RPC defaults in the desktop application

## Completed source cleanup

- Removed inherited Monero mainnet checkpoints
- Removed inherited Monero DNS and IP seed nodes
- Added native support for eight-decimal FRG formatting
- Preserved the Phase 3 genesis, network UUID, rewards, and emission policy

## Before broad public-value use

- Obtain independent review of fork-specific consensus and wallet changes
- Publish stable seed nodes operated by more than one party
- Produce signed, reproducible release builds
- Create ForgeCoin-specific testnet and stagenet identities
- Test upgrades, reorganizations, backup recovery, and multi-node synchronization
- Establish multiple independent miners and pools
- Document the spendability and intended treatment of the genesis transaction output
