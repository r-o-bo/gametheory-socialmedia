import unittest

from game_theory import INVEST, MAINTAIN, Game, simulate


class TestOneShot(unittest.TestCase):
    def setUp(self):
        self.g = Game()

    def test_invest_strictly_dominant(self):
        self.assertEqual(self.g.strictly_dominant(0), INVEST)
        self.assertEqual(self.g.strictly_dominant(1), INVEST)

    def test_unique_nash_is_mutual_invest(self):
        self.assertEqual(self.g.pure_nash(), [(INVEST, INVEST)])

    def test_pareto_includes_mutual_maintain_not_nash(self):
        pareto = self.g.pareto_optimal()
        self.assertIn((MAINTAIN, MAINTAIN), pareto)
        self.assertNotIn((INVEST, INVEST), pareto)

    def test_is_prisoners_dilemma(self):
        self.assertTrue(self.g.is_prisoners_dilemma())

    def test_collusion_threshold(self):
        self.assertAlmostEqual(self.g.collusion_threshold(), 0.5)

    def test_no_dominance_when_payoffs_change(self):
        # Coordination-style game: no dominant strategy, two pure Nash equilibria.
        g = Game({
            (INVEST, INVEST): (4, 4), (INVEST, MAINTAIN): (1, 1),
            (MAINTAIN, INVEST): (1, 1), (MAINTAIN, MAINTAIN): (3, 3),
        })
        self.assertIsNone(g.strictly_dominant(0))
        self.assertEqual(len(g.pure_nash()), 2)
        self.assertFalse(g.is_prisoners_dilemma())

    def test_invalid_payoffs(self):
        with self.assertRaises(ValueError):
            Game({(INVEST, INVEST): (1, 1)})


class TestRepeated(unittest.TestCase):
    def setUp(self):
        self.g = Game()

    def test_tft_pair_sustains_cooperation(self):
        r = simulate(self.g, "tit_for_tat", "tit_for_tat", rounds=10)
        self.assertEqual(r["total_A"], 40)
        self.assertEqual(r["total_B"], 40)

    def test_always_invest_pair_stuck_at_nash(self):
        r = simulate(self.g, "always_invest", "always_invest", rounds=10)
        self.assertEqual(r["total_A"], 30)

    def test_tft_punishes_exploiter(self):
        r = simulate(self.g, "tit_for_tat", "always_invest", rounds=5)
        # Round 1: (1, 5), then (3, 3) x4
        self.assertEqual(r["total_A"], 1 + 3 * 4)
        self.assertEqual(r["total_B"], 5 + 3 * 4)

    def test_discounting(self):
        r = simulate(self.g, "always_maintain", "always_maintain", rounds=2, discount=0.5)
        self.assertAlmostEqual(r["total_A"], 4 + 2)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            simulate(self.g, "nope", "tit_for_tat")
        with self.assertRaises(ValueError):
            simulate(self.g, "tit_for_tat", "tit_for_tat", rounds=0)


if __name__ == "__main__":
    unittest.main()
