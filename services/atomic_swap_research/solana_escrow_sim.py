"""OFFLINE Solana-side swap escrow state machine for protocol design tests.

Not a deployed Solana program. No cryptographic key proof, no token transfers,
no RPC/keys, no cross-chain verification. Simulates mutually exclusive claim
and refund paths and two deadline windows for SOL/original-program SPL assets.
The eventual FCMP++/CARROT secret-share construction requires separate proof.
"""
from dataclasses import dataclass
from enum import Enum


class EscrowRejected(ValueError):
    pass


class Stage(str, Enum):
    LOCKED = "LOCKED"
    READY = "READY"
    CLAIMED = "CLAIMED"
    REFUNDED = "REFUNDED"


class AssetKind(str, Enum):
    SOL = "SOL"
    SPL = "SPL"  # Legacy/original SPL Token Program, including Solana USDC


ORIGINAL_SPL_TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
U64_MAX = 2**64 - 1


@dataclass(frozen=True)
class EscrowSpec:
    swap_id: str
    owner: str
    recipient: str
    asset_kind: AssetKind
    asset_mint: str | None
    amount_atomic: int
    created_at: int
    t0: int
    t1: int

    def __post_init__(self) -> None:
        if not self.swap_id or not self.owner or not self.recipient or self.owner == self.recipient:
            raise EscrowRejected("unique swap id and distinct parties required")
        if self.asset_kind not in (AssetKind.SOL, AssetKind.SPL):
            raise EscrowRejected("unsupported asset; Ethereum/ERC-20 not accepted")
        if self.asset_kind == AssetKind.SOL and self.asset_mint is not None:
            raise EscrowRejected("native SOL cannot specify SPL mint")
        if self.asset_kind == AssetKind.SPL and not self.asset_mint:
            raise EscrowRejected("SPL asset requires verified mint and original token program")
        if type(self.amount_atomic) is not int or not 0 < self.amount_atomic <= U64_MAX:
            raise EscrowRejected("Solana atomic amount must be positive u64")
        if any(type(x) is not int for x in (self.created_at, self.t0, self.t1)):
            raise EscrowRejected("timestamps must be integer")
        if not self.created_at < self.t0 < self.t1:
            raise EscrowRejected("require creation < first timeout < second timeout")


class Escrow:
    """Test model. Token ownership and revealed secrets are NOT verified here."""

    def __init__(self, spec: EscrowSpec) -> None:
        self.spec = spec
        self.stage = Stage.LOCKED

    def ready(self, actor: str, now: int, *, remote_lock_confirmed: bool) -> None:
        if actor != self.spec.owner:
            raise EscrowRejected("only Solana escrow owner can set ready")
        if self.stage != Stage.LOCKED:
            raise EscrowRejected("ready only allowed from locked")
        if type(now) is not int or now >= self.spec.t0:
            raise EscrowRejected("ready deadline elapsed")
        if remote_lock_confirmed is not True:
            raise EscrowRejected("explicit simulated remote-lock confirmation required")
        self.stage = Stage.READY

    def claim(self, actor: str, now: int, *, secret_proof_verified: bool) -> None:
        if actor != self.spec.recipient:
            raise EscrowRejected("only registered recipient can claim")
        if self.stage not in (Stage.LOCKED, Stage.READY):
            raise EscrowRejected("escrow already settled")
        if type(now) is not int or now >= self.spec.t1:
            raise EscrowRejected("claim deadline elapsed")
        if self.stage != Stage.READY and now < self.spec.t0:
            raise EscrowRejected("claim must wait for ready or first timeout")
        if secret_proof_verified is not True:
            raise EscrowRejected("no validated secret/public point linkage")
        self.stage = Stage.CLAIMED

    def refund(self, actor: str, now: int, *, refund_proof_verified: bool) -> None:
        if actor != self.spec.owner:
            raise EscrowRejected("only depositor can refund")
        if self.stage not in (Stage.LOCKED, Stage.READY):
            raise EscrowRejected("escrow already settled")
        if type(now) is not int:
            raise EscrowRejected("invalid clock")
        if self.stage == Stage.READY and now < self.spec.t1:
            raise EscrowRejected("ready escrow cannot refund before final timeout")
        if self.spec.t0 <= now < self.spec.t1:
            raise EscrowRejected("refund is forbidden during claim window")
        if refund_proof_verified is not True:
            raise EscrowRejected("refund secret/public point linkage unverified")
        self.stage = Stage.REFUNDED


def request_real_solana_swap() -> None:
    raise NotImplementedError(
        "No deployed Solana escrow, Curve25519 proof, locked native FRG, "
        "FCMP++/CARROT compatibility, or audited cross-chain swap exists."
    )
