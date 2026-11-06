"""Game-theoretic model of social media content competition.

Two symmetric platforms (A, B) simultaneously choose Invest or Maintain.
Payoffs are (payoff_A, payoff_B). Pure standard-library, no dependencies.
"""

from __future__ import annotations

from itertools import product

INVEST, MAINTAIN = "Invest", "Maintain"
ACTIONS = (INVEST, MAINTAIN)

# Illustrative payoffs from the slides (not measured data).
DEFAULT_PAYOFFS = {
    (INVEST, INVEST): (3, 3),
    (INVEST, MAINTAIN): (5, 1),
    (MAINTAIN, INVEST): (1, 5),
    (MAINTAIN, MAINTAIN): (4, 4),
}


class Game:
    """A 2x2 normal-form game between platforms A (row) and B (column)."""

    def __init__(self, payoffs=None):
        payoffs = dict(payoffs or DEFAULT_PAYOFFS)
        expected = set(product(ACTIONS, ACTIONS))
        if set(payoffs) != expected:
            raise ValueError("payoffs must define all four action profiles")
        for profile, pair in payoffs.items():
            if len(pair) != 2 or not all(isinstance(x, (int, float)) for x in pair):
                raise ValueError(f"payoff for {profile} must be two numbers")
        self.payoffs = {k: tuple(v) for k, v in payoffs.items()}

    # ---- basic accessors -------------------------------------------------
    def payoff(self, a: str, b: str):
        return self.payoffs[(a, b)]

    def utility(self, player: int, own: str, other: str) -> float:
        """player 0 = A, 1 = B; `other` is the rival's action."""
        profile = (own, other) if player == 0 else (other, own)
        return self.payoffs[profile][player]

    # ---- solution concepts -----------------------------------------------
    def best_responses(self, player: int, other: str):
        best = max(self.utility(player, a, other) for a in ACTIONS)
        return [a for a in ACTIONS if self.utility(player, a, other) == best]

    def strictly_dominant(self, player: int):
        for a in ACTIONS:
            rival = MAINTAIN if a == INVEST else INVEST
            if all(self.utility(player, a, o) > self.utility(player, rival, o) for o in ACTIONS):
                return a
        return None

    def pure_nash(self):
        return [
            (a, b)
            for a, b in product(ACTIONS, ACTIONS)
            if a in self.best_responses(0, b) and b in self.best_responses(1, a)
        ]

    def pareto_optimal(self):
        profiles = list(self.payoffs)
        def dominated(p):
            pa, pb = self.payoffs[p]
            return any(
                qa >= pa and qb >= pb and (qa > pa or qb > pb)
                for q in profiles
                for qa, qb in [self.payoffs[q]]
            )
        return [p for p in profiles if not dominated(p)]

    # ---- Prisoner's Dilemma structure --------------------------------------
    def pd_values(self):
        """Return T, R, P, S with Invest as 'defect' and Maintain as 'cooperate'."""
        return {
            "T": self.payoffs[(INVEST, MAINTAIN)][0],    # temptation
            "R": self.payoffs[(MAINTAIN, MAINTAIN)][0],  # reward
            "P": self.payoffs[(INVEST, INVEST)][0],      # punishment
            "S": self.payoffs[(MAINTAIN, INVEST)][0],    # sucker
        }

    def is_prisoners_dilemma(self) -> bool:
        v = self.pd_values()
        symmetric = all(
            self.payoffs[(a, b)] == self.payoffs[(b, a)][::-1] for a, b in product(ACTIONS, ACTIONS)
        )
        return symmetric and v["T"] > v["R"] > v["P"] > v["S"] and 2 * v["R"] > v["T"] + v["S"]

    def collusion_threshold(self):
        """Minimum discount factor for grim-trigger to sustain (Maintain, Maintain).

        delta >= (T - R) / (T - P). Returns None if not a PD-like game.
        """
        v = self.pd_values()
        if v["T"] <= v["P"]:
            return None
        return max(0.0, (v["T"] - v["R"]) / (v["T"] - v["P"]))

    def analyze(self) -> dict:
        dom = [self.strictly_dominant(0), self.strictly_dominant(1)]
        nash = self.pure_nash()
        pareto = self.pareto_optimal()
        return {
            "payoffs": {f"{a}|{b}": list(p) for (a, b), p in self.payoffs.items()},
            "best_responses": {
                "A": {o: self.best_responses(0, o) for o in ACTIONS},
                "B": {o: self.best_responses(1, o) for o in ACTIONS},
            },
            "dominant": {"A": dom[0], "B": dom[1]},
            "nash": [list(p) for p in nash],
            "pareto": [list(p) for p in pareto],
            "nash_is_pareto_efficient": all(p in pareto for p in nash) if nash else None,
            "is_prisoners_dilemma": self.is_prisoners_dilemma(),
            "pd_values": self.pd_values(),
            "collusion_threshold": self.collusion_threshold(),
        }


# ---- repeated-game simulation ----------------------------------------------
def always_invest(own, opp):
    return INVEST


def always_maintain(own, opp):
    return MAINTAIN


def tit_for_tat(own, opp):
    return MAINTAIN if not opp else opp[-1]


def grim_trigger(own, opp):
    return INVEST if INVEST in opp else MAINTAIN


STRATEGIES = {
    "always_invest": always_invest,
    "always_maintain": always_maintain,
    "tit_for_tat": tit_for_tat,
    "grim_trigger": grim_trigger,
}


def simulate(game: Game, strat_a: str, strat_b: str, rounds: int = 20, discount: float = 1.0):
    """Play a repeated game. Returns per-round history plus total (discounted) payoffs."""
    if strat_a not in STRATEGIES or strat_b not in STRATEGIES:
        raise ValueError(f"strategies must be one of {sorted(STRATEGIES)}")
    if not 1 <= rounds <= 1000:
        raise ValueError("rounds must be between 1 and 1000")
    if not 0 < discount <= 1:
        raise ValueError("discount must be in (0, 1]")

    hist_a, hist_b, rows = [], [], []
    total_a = total_b = 0.0
    for t in range(rounds):
        a = STRATEGIES[strat_a](hist_a, hist_b)
        b = STRATEGIES[strat_b](hist_b, hist_a)
        pa, pb = game.payoff(a, b)
        w = discount ** t
        total_a += w * pa
        total_b += w * pb
        hist_a.append(a)
        hist_b.append(b)
        rows.append({"round": t + 1, "A": a, "B": b, "payoff_A": pa, "payoff_B": pb})
    return {"history": rows, "total_A": round(total_a, 4), "total_B": round(total_b, 4)}
