"""OFFLINE ONLY: deterministic RFQ matching and settlement previews.

Not an exchange, private order book, atomic swap, confidential computation,
TSS implementation, wallet or live asset ledger. No keys and no network calls.
Production custody and order execution are deliberately unavailable.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Literal
import json

Side = Literal["BUY_BASE", "SELL_BASE"]


class RejectedOrder(ValueError):
    """An offer pair or simulated settlement violates protocol policy."""


class ProductionIntegrationBlocked(RuntimeError):
    """Required cryptographic or consensus verification is unavailable."""


@dataclass(frozen=True)
class OrderIntent:
    order_id: str
    participant: str
    side: Side
    base_asset: str
    quote_asset: str
    base_units: int
    quote_units: int
    expires_at: int
    nonce: str

    def validate(self, now: int) -> None:
        if not self.order_id or not self.participant or not self.nonce:
            raise RejectedOrder("order identifiers/nonce must be nonempty")
        if self.side not in ("BUY_BASE", "SELL_BASE"):
            raise RejectedOrder("invalid side")
        if not self.base_asset or not self.quote_asset or self.base_asset == self.quote_asset:
            raise RejectedOrder("pair must contain two distinct assets")
        if (type(self.base_units) is not int or type(self.quote_units) is not int
                or self.base_units <= 0 or self.quote_units <= 0):
            raise RejectedOrder("strictly positive integer atomic-unit quantities required")
        if type(self.expires_at) is not int or self.expires_at <= now:
            raise RejectedOrder("expired offer")


@dataclass(frozen=True)
class ThresholdVaultPolicy:
    """Threshold *policy*, not a TSS signer or proof of actual decentralization."""

    vault_label: str
    chain_id: str
    signer_ids: tuple[str, ...]
    threshold: int

    def __post_init__(self) -> None:
        if (not self.vault_label or not self.chain_id
                or not self.signer_ids or len(set(self.signer_ids)) != len(self.signer_ids)
                or not all(self.signer_ids)
                or type(self.threshold) is not int
                or not 1 < self.threshold <= len(self.signer_ids)):
            raise RejectedOrder("invalid signer quorum configuration")

    def check_declared_quorum(self, signer_ids: tuple[str, ...]) -> bool:
        """Research only: compares names; does NOT verify threshold signatures."""
        return (len(signer_ids) == len(set(signer_ids))
                and len(signer_ids) >= self.threshold
                and set(signer_ids).issubset(self.signer_ids))


@dataclass(frozen=True)
class SettlementPreview:
    sell_order_id: str
    buy_order_id: str
    base_asset: str
    quote_asset: str
    base_units: int
    quote_units: int
    fee_units: int
    seller_quote_receives: int
    # Deltas are positive credits, negative debits, *not actual balances*.
    buyer_base_delta: int
    buyer_quote_delta: int
    seller_base_delta: int
    seller_quote_delta: int
    treasury_quote_delta: int

    def assert_conserved(self) -> None:
        if self.buyer_base_delta + self.seller_base_delta != 0:
            raise RejectedOrder("base conservation failed")
        if (self.buyer_quote_delta + self.seller_quote_delta
                + self.treasury_quote_delta != 0):
            raise RejectedOrder("quote conservation failed")


def preview_exact_match(
    sell: OrderIntent, buy: OrderIntent, *, now: int, fee_bps: int
) -> SettlementPreview:
    """Fail-closed exact RFQ match; intentionally no partial fills or floating math."""
    sell.validate(now)
    buy.validate(now)
    if sell.side != "SELL_BASE" or buy.side != "BUY_BASE":
        raise RejectedOrder("expected seller and buyer order")
    if sell.participant == buy.participant:
        raise RejectedOrder("self-trades are forbidden")
    if sell.order_id == buy.order_id or sell.nonce == buy.nonce:
        raise RejectedOrder("duplicate order id or nonce")
    if (sell.base_asset != buy.base_asset or sell.quote_asset != buy.quote_asset
            or sell.base_units != buy.base_units or sell.quote_units != buy.quote_units):
        raise RejectedOrder("full-fill amounts and asset pair must match exactly")
    if type(fee_bps) is not int or not 0 <= fee_bps < 10_000:
        raise RejectedOrder("fee_bps must be an integer in [0, 10000)")
    # ceil division: fee always accounts for nonzero fractional units.
    fee = (sell.quote_units * fee_bps + 9999) // 10000
    if fee >= sell.quote_units:
        raise RejectedOrder("fee consumes settlement proceeds")
    preview = SettlementPreview(
        sell.order_id, buy.order_id, sell.base_asset, sell.quote_asset,
        sell.base_units, sell.quote_units, fee, sell.quote_units - fee,
        sell.base_units, -sell.quote_units, -sell.base_units,
        sell.quote_units - fee, fee,
    )
    preview.assert_conserved()
    return preview


def order_commitment(intent: OrderIntent) -> str:
    """Illustrative domain-separated hash, NOT encryption/anonymity/ZK validity."""
    payload = json.dumps({
        "v": 1, "domain": "forgecoin-dark-pool-research-only",
        "id": intent.order_id, "party": intent.participant, "side": intent.side,
        "base": intent.base_asset, "quote": intent.quote_asset,
        "base_units": intent.base_units, "quote_units": intent.quote_units,
        "expiry": intent.expires_at, "nonce": intent.nonce,
    }, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(payload).hexdigest()


def request_custodial_settlement(*_args: object, **_kwargs: object) -> None:
    """Production MUST bind proof, settlement and TSS to signed chain operations."""
    raise ProductionIntegrationBlocked(
        "No TSS implementation, on-chain vault, order signature verification, "
        "asset custody, or FCMP++ cross-chain proof exists"
    )


def request_blind_relay(*_args: object, **_kwargs: object) -> None:
    raise ProductionIntegrationBlocked(
        "No authenticated encrypted relay, unlinkable proof, or privacy audit exists"
    )
