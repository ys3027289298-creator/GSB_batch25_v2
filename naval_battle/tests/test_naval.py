import copy
import unittest

import core
import world


class TestDomainBehavior(unittest.TestCase):
    def test_duplicate_ship_rejected(self):
        state = world.new_game()
        self.assertTrue(core.action_a(state, "cruiser-1"))
        self.assertFalse(core.action_a(state, "cruiser-1"))
        self.assertEqual(len(state["ships"]), 1)

    def test_form_fleet_rejected_when_full(self):
        state = world.new_game()
        state["fleet"] = ["a", "b"]
        state["staging"] = "c"
        self.assertFalse(core.action_b(state))
        self.assertEqual(state["fleet"], ["a", "b"])
        self.assertEqual(state["staging"], "c")

    def test_form_fleet_requires_waiting_ship(self):
        state = world.new_game()
        self.assertFalse(core.action_b(state))
        self.assertEqual(state["fleet"], [])

    def test_empty_sea_returns_false(self):
        state = world.new_game()
        self.assertFalse(core.action_d(state, (0, 0)))

    def test_attack_earliest_arrival(self):
        state = world.new_game()
        state["events"] = {1: (5, 6), 2: (1, 2)}
        self.assertEqual(core.action_c(state), 2)

    def test_paused_fleet_does_not_advance(self):
        state = world.new_game()
        state["paused"] = True
        self.assertFalse(core.action_j(state))
        state["paused"] = False
        self.assertTrue(core.action_j(state))

    def test_view_ship_does_not_remove(self):
        state = world.new_game()
        state["queue"] = [1, 2]
        self.assertEqual(core.action_f(state), 1)
        self.assertEqual(state["queue"], [1, 2])

    def test_ammo_counted_exactly(self):
        state = world.new_game()
        state["items"] = ["shell", "shell", "shell"]
        self.assertEqual(core.action_g(state), 3)

    def test_single_round_settled_once(self):
        state = world.new_game()
        self.assertTrue(core.action_e(state))
        self.assertFalse(core.action_e(state))

    def test_id_sequence_does_not_skip(self):
        state = world.new_game()
        state["next_id"] = 7
        self.assertEqual(core.action_h(state), 7)
        self.assertEqual(core.action_h(state), 7)

    def test_reset_clears_results(self):
        state = world.new_game()
        state["src"] = 30
        self.assertTrue(core.action_i(state, 10))
        self.assertEqual((state["src"], state["dst"]), (20, 10))
        state["src"] = 5
        self.assertFalse(core.action_i(state, 10))
        self.assertEqual((state["src"], state["dst"]), (5, 10))


class TestFailureRollback(unittest.TestCase):
    def _assert_unchanged(self, before, state):
        self.assertEqual(before, state)

    def test_duplicate_ship_rolls_back(self):
        state = world.new_game()
        core.action_a(state, "d-1")
        before = copy.deepcopy(state)
        self.assertFalse(core.action_a(state, "d-1"))
        self._assert_unchanged(before, state)

    def test_full_fleet_rolls_back(self):
        state = world.new_game()
        state["fleet"] = ["a", "b"]
        state["staging"] = "c"
        before = copy.deepcopy(state)
        self.assertFalse(core.action_b(state))
        self._assert_unchanged(before, state)

    def test_empty_sea_rolls_back(self):
        state = world.new_game()
        before = copy.deepcopy(state)
        self.assertFalse(core.action_d(state, (9, 9)))
        self._assert_unchanged(before, state)

    def test_settled_round_rolls_back(self):
        state = world.new_game()
        core.action_e(state)
        before = copy.deepcopy(state)
        self.assertFalse(core.action_e(state))
        self._assert_unchanged(before, state)

    def test_insufficient_supply_rolls_back(self):
        state = world.new_game()
        state["src"] = 5
        state["dst"] = 3
        before = copy.deepcopy(state)
        self.assertFalse(core.action_i(state, 10))
        self._assert_unchanged(before, state)

    def test_empty_queue_view_rolls_back(self):
        state = world.new_game()
        before = copy.deepcopy(state)
        self.assertIsNone(core.action_f(state))
        self._assert_unchanged(before, state)

    def test_paused_advance_rolls_back(self):
        state = world.new_game()
        state["paused"] = True
        before = copy.deepcopy(state)
        self.assertFalse(core.action_j(state))
        self._assert_unchanged(before, state)


class TestReplay(unittest.TestCase):
    def _scenario(self):
        state = world.new_game()
        commands = [
            (core.action_a, ("cruiser",)),
            (core.action_a, ("cruiser",)),
            (core.action_a, ("destroyer",)),
            (core.action_b, ("cruiser",)),
            (core.action_b, ("destroyer",)),
            (core.action_b, ("frigate",)),
            (core.action_c, ()),
            (core.action_d, ((0, 0),)),
            (core.action_f, ()),
            (core.action_g, ()),
            (core.action_h, ()),
            (core.action_e, ()),
            (core.action_e, ()),
            (core.action_i, (10,)),
            (core.action_j, ()),
        ]
        state["events"] = {1: (5, 6), 2: (1, 2)}
        state["queue"] = [9]
        state["items"] = ["x", "y"]
        state["next_id"] = 4
        state["src"] = 25
        return state, commands

    def test_replay_matches_original(self):
        original, commands = self._scenario()
        snapshot = copy.deepcopy(original)
        first_results = [fn(original, *args) for fn, args in commands]
        first_state = copy.deepcopy(original)

        replay, replay_commands = self._scenario()
        self.assertEqual(snapshot, replay)
        replay_results = [fn(replay, *args) for fn, args in replay_commands]

        self.assertEqual(first_results, replay_results)
        self.assertEqual(first_state, replay)

    def test_replay_failed_commands_is_stable(self):
        state, commands = self._scenario()
        failures = []
        for fn, args in commands:
            if not fn(state, *args):
                failures.append((fn, args))
        settled = copy.deepcopy(state)
        replay, replay_commands = self._scenario()
        replay_failures = []
        for fn, args in replay_commands:
            if not fn(replay, *args):
                replay_failures.append((fn, args))
        for fn, args in replay_failures:
            self.assertFalse(fn(replay, *args))
        self.assertEqual(failures, replay_failures)
        self.assertEqual(settled, replay)


if __name__ == "__main__":
    unittest.main()
