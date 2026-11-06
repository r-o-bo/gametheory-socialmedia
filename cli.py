"""Command-line interface: python cli.py [analyze|simulate] ..."""

import argparse

from game_theory import ACTIONS, DEFAULT_PAYOFFS, STRATEGIES, Game, simulate


def print_matrix(game: Game):
    print(f"\n{'A \\ B':<12}" + "".join(f"{b:<12}" for b in ACTIONS))
    for a in ACTIONS:
        print(f"{a:<12}" + "".join(f"{str(game.payoff(a, b)):<12}" for b in ACTIONS))


def cmd_analyze(args):
    game = Game()
    r = game.analyze()
    print_matrix(game)
    print("\nStrictly dominant strategy:", r["dominant"])
    print("Pure Nash equilibria:     ", [tuple(p) for p in r["nash"]])
    print("Pareto-optimal profiles:  ", [tuple(p) for p in r["pareto"]])
    print("Nash is Pareto-efficient: ", r["nash_is_pareto_efficient"])
    print("Prisoner's Dilemma:       ", r["is_prisoners_dilemma"])
    if r["collusion_threshold"] is not None:
        print(f"Grim-trigger collusion needs discount factor >= {r['collusion_threshold']:.2f}")


def cmd_simulate(args):
    res = simulate(Game(), args.a, args.b, args.rounds, args.discount)
    for row in res["history"]:
        print(f"round {row['round']:>3}: A={row['A']:<9} B={row['B']:<9} -> ({row['payoff_A']}, {row['payoff_B']})")
    print(f"\nTotals: A={res['total_A']}  B={res['total_B']}")


def main():
    p = argparse.ArgumentParser(description="Social media content competition game")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("analyze", help="analyze the one-shot game").set_defaults(fn=cmd_analyze)
    s = sub.add_parser("simulate", help="simulate the repeated game")
    s.add_argument("--a", choices=STRATEGIES, default="tit_for_tat")
    s.add_argument("--b", choices=STRATEGIES, default="always_invest")
    s.add_argument("--rounds", type=int, default=10)
    s.add_argument("--discount", type=float, default=1.0)
    s.set_defaults(fn=cmd_simulate)
    args = p.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
