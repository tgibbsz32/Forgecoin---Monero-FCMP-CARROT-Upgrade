# Native FRG bonding: wallet construction gate

**Status:** read-only finding, 2026-10-22. No consensus or wallet change; no funded locking.

## Observed source behavior

The ordinary native FRG wallet currently **does not expose a supported nonzero unlock-time transfer**:

- `src/wallet/wallet_rpc_server.cpp`: transfer handlers reject requests with `unlock_time != 0`, returning `WALLET_RPC_ERROR_CODE_NONZERO_UNLOCK_TIME` and the message `Transaction cannot have non-zero unlock time`. The guarded handlers include the transfer and transfer-split paths around lines 1247 and 1307, as well as others around 1760 and 1826.
- `src/wallet/wallet2.cpp`: unsigned transaction signing rejects `sd.unlock_time` through `error::nonzero_unlock_time` around line 7836. Ordinary construction data sets unlock time to zero around lines 10049 and 10403.
- `src/cryptonote_core/cryptonote_tx_utils.cpp`: an ordinary transaction construction path sets `tx.unlock_time = 0` around line 260.
- `src/cryptonote_core/blockchain.cpp`: consensus-side spend-time unlock checks exist, including height/time leeway. Their existence **does not** authorize bypassing wallet validation or prove enforceable, verifiable bonds.

These line references describe the reviewed code revision and may shift in later edits.

## Decision for the miner governance project

**Block implementation of native FRG bond deposits and binding miner-bond voting.** Do not remove wallet guards or expose unsafe custom transaction construction as an implementation shortcut.

A proposal must first show, using an independently reviewed isolated fork/testnet:
1. A consensus-compatible and wallet-recoverable enforceable lock with a precisely calculated earliest spending boundary.
2. Independently verifiable proof of amount, ownership, uniqueness and continued unspent status consistent with RingCT/privacy.
3. Safe unbonding, reorg handling, mining evidence and suspension rules.
4. Security review and separate approval of any changed native wallet or protocol rules.

If a credible privacy-safe native bond cannot be demonstrated, reconsider bonded governance eligibility in a constitutional proposal rather than substituting a signed pledge or a custodial promise without disclosure.

**Regtest status:** prior isolated wallet test successfully recognized mature FRG at chain height 67; a nonzero unlock-time bond has not been created or tested. Existing wallet rejection is a source-grounded blocker.
