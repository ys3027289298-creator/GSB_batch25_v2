import unittest

import world


class TestWorld(unittest.TestCase):
    def test_case_a(self):
        state = world.new_game()
        state.update({'events': {}})
        self.assertTrue(world.action_a(state))
        self.assertFalse(world.action_a(state))

    def test_case_b(self):
        state = world.new_game()
        self.assertFalse(world.action_b(state))

    def test_case_c(self):
        state = world.new_game()
        state.update({'events': {1: (5, 6), 2: (1, 2)}})
        self.assertEqual(world.action_c(state), 2)

    def test_case_d(self):
        state = world.new_game()
        self.assertFalse(world.action_d(state))

    def test_case_e(self):
        state = world.new_game()
        self.assertTrue(world.action_e(state))
        self.assertFalse(world.action_e(state))

    def test_case_f(self):
        state = world.new_game()
        state.update({'queue': []})
        state["queue"] = [1, 2]
        self.assertEqual(world.action_f(state), 1)

    def test_case_g(self):
        state = world.new_game()
        state.update({'items': []})
        state["items"] = [1]
        self.assertEqual(world.action_g(state), 1)

    def test_case_h(self):
        state = world.new_game()
        state.update({'next_id': 1})
        state["next_id"] = 7
        self.assertEqual(world.action_h(state), 7)

    def test_case_i(self):
        state = world.new_game()
        state.update({'src': 5, 'dst': 0})
        world.action_i(state)
        self.assertEqual(state["src"], 5)

    def test_case_j(self):
        state = world.new_game()
        state.update({'closed': False})
        state["closed"] = True
        self.assertFalse(world.action_j(state))


if __name__ == "__main__":
    unittest.main()


import copy


class TestRollbackAndReplay(unittest.TestCase):
    def test_failure_rollback(self):
        state = world.new_game()
        before = copy.deepcopy(state)
        self.assertFalse(world.action_b(state))
        self.assertFalse(world.action_d(state))
        state["paused"] = True
        self.assertFalse(world.action_e(state))
        state["closed"] = True
        self.assertFalse(world.action_j(state))
        state["paused"] = before["paused"]
        state["closed"] = before["closed"]
        self.assertEqual(state, before)
        self.assertTrue(world.action_a(state))
        ships_snapshot = copy.deepcopy(state["ships"])
        self.assertFalse(world.action_a(state))
        self.assertEqual(state["ships"], ships_snapshot)

    def test_replay(self):
        def run():
            state = world.new_game()
            world.action_a(state)
            world.action_e(state)
            world.action_d(state)
            state["events"] = {1: (5, 6), 2: (1, 2)}
            world.action_c(state)
            world.action_i(state)
            return state

        first = run()
        second = run()
        self.assertEqual(first, second)
        self.assertEqual(first["hits"], 0)
        self.assertEqual(first["dst"], 0)
