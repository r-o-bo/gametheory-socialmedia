# Social Media Content Competition: Game Theory App

A small, dependency-free Python app that implements the model from the
"Game Theory-Based Analysis of Social Media Content Competition" slides.

Two symmetric platforms (A, B) simultaneously choose **Invest** or **Maintain**.
Default payoffs (illustrative, not measured data):

| A \ B    | Invest | Maintain |
|----------|--------|----------|
| Invest   | (3, 3) | (5, 1)   |
| Maintain | (1, 5) | (4, 4)   |

The app shows that Invest strictly dominates, (Invest, Invest) is the unique
Nash equilibrium, and (Maintain, Maintain) is Pareto-superior: a Prisoner's Dilemma.
It also covers the slides' "repeated games" critique: with grim trigger,
cooperation is sustainable when the discount factor is at least (T-R)/(T-P) = 0.5.

## Run

Requires Python 3.8+. No packages to install.

```bash
python cli.py analyze
python cli.py simulate --a tit_for_tat --b always_invest --rounds 10 --discount 0.9
python server.py 8000        # then open http://localhost:8000
python -m unittest -v        # run tests
```

## Layout

- `game_theory.py`: engine (dominance, best responses, Nash, Pareto, PD test, repeated-game simulator)
- `cli.py`: command-line interface
- `server.py` + `static/index.html`: web UI with editable payoff matrix; JSON API at `/api/analyze` and `/api/simulate`
- `test_game_theory.py`: unit tests

Strategies: `always_invest`, `always_maintain`, `tit_for_tat`, `grim_trigger`.
