"""Offline accounting and capacity model; no mining or network access."""
from dataclasses import dataclass

MAX_WORKERS = 100
FEE_BPS = 100


class CapacityExceeded(Exception):
    pass


class WorkerRegistry:
    def __init__(self, limit=MAX_WORKERS):
        if not 1 <= limit <= MAX_WORKERS:
            raise ValueError("limit must be 1..100")
        self.limit = limit
        self.active = set()

    def connect(self, connection_id):
        if not connection_id:
            raise ValueError("nonempty ID required")
        if connection_id in self.active:
            return False
        if len(self.active) >= self.limit:
            raise CapacityExceeded("worker capacity reached")
        self.active.add(connection_id)
        return True

    def disconnect(self, connection_id):
        self.active.discard(connection_id)


@dataclass(frozen=True)
class Allocation:
    fee_atomic: int
    miner_atomic: dict[str, int]


def allocate_reward(reward_atomic: int, shares: dict[str, int]) -> Allocation:
    """Simulation only: deterministic proportional weights and 1% operator fee.

    Not a Stratum server, PPLNS engine, maturity verifier or payout executor.
    """
    if type(reward_atomic) is not int or reward_atomic < 0:
        raise ValueError("reward must be a nonnegative integer")
    if not shares or any(not k or type(v) is not int or v < 0 for k, v in shares.items()):
        raise ValueError("invalid shares")
    total = sum(shares.values())
    if not total:
        raise ValueError("no earned shares")
    fee = reward_atomic * FEE_BPS // 10_000
    net = reward_atomic - fee
    amounts = {k: net * v // total for k, v in shares.items()}
    left = net - sum(amounts.values())
    rank = sorted(shares, key=lambda k: (-(net * shares[k] % total), k))
    for k in rank[:left]:
        amounts[k] += 1
    assert fee + sum(amounts.values()) == reward_atomic
    return Allocation(fee, amounts)
