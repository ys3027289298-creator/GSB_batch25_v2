import copy
import unittest

import main


class TestMain(unittest.TestCase):
    def test_case_a(self):
        state = main.new_game()
        state.update({'items': []})
        state["items"] = [1]
        self.assertEqual(main.cmd_a(state), 1)

    def test_case_b(self):
        state = main.new_game()
        state.update({'next_id': 1})
        state["next_id"] = 7
        self.assertEqual(main.cmd_b(state), 7)

    def test_case_c(self):
        state = main.new_game()
        state.update({'src': 5, 'dst': 0})
        main.cmd_c(state)
        self.assertEqual(state["src"], 5)

    def test_case_d(self):
        state = main.new_game()
        state.update({'closed': False})
        state["closed"] = True
        self.assertFalse(main.cmd_d(state))

    def test_case_e(self):
        state = main.new_game()
        state.update({'events': {}})
        self.assertTrue(main.cmd_e(state))
        self.assertFalse(main.cmd_e(state))

    def test_case_f(self):
        state = main.new_game()
        self.assertFalse(main.cmd_f(state))

    def test_case_g(self):
        state = main.new_game()
        state.update({'events': {1: (5, 6), 2: (1, 2)}})
        self.assertEqual(main.cmd_g(state), 2)

    def test_case_h(self):
        state = main.new_game()
        self.assertFalse(main.cmd_h(state))

    def test_case_i(self):
        state = main.new_game()
        self.assertTrue(main.cmd_i(state))
        self.assertFalse(main.cmd_i(state))

    def test_case_j(self):
        state = main.new_game()
        state.update({'queue': []})
        state["queue"] = [1, 2]
        self.assertEqual(main.cmd_j(state), 1)

    def _full_state(self):
        state = main.new_game()
        state.update({
            'items': [1, 2, 3],
            'next_id': 7,
            'src': 20,
            'dst': 0,
            'closed': False,
            'requested': False,
            'events': {1: (5, 6), 2: (1, 2)},
            'records': [9],
            'ran': False,
            'queue': [1, 2],
        })
        return state

    def _run_sequence(self, state):
        results = []
        results.append(main.cmd_a(state))
        results.append(main.cmd_b(state))
        results.append(main.cmd_c(state))
        results.append(main.cmd_d(state))
        results.append((main.cmd_e(state), main.cmd_e(state)))
        results.append(main.cmd_f(state))
        results.append(main.cmd_g(state))
        results.append(main.cmd_h(state))
        results.append((main.cmd_i(state), main.cmd_i(state)))
        results.append(main.cmd_j(state))
        return results

    def test_replay_from_snapshot_is_identical(self):
        snapshot = self._full_state()
        first = self._run_sequence(copy.deepcopy(snapshot))
        replayed = self._run_sequence(copy.deepcopy(snapshot))
        self.assertEqual(first, replayed)
        end_first = self._run_sequence(copy.deepcopy(snapshot))
        self.assertEqual(end_first, replayed)

    def test_replay_does_not_skip_or_reuse_ids(self):
        state = self._full_state()
        self.assertEqual(main.cmd_b(state), 7)
        restored = self._full_state()
        self.assertEqual(main.cmd_b(restored), 7)
        self.assertEqual(restored["next_id"], 8)
        self.assertEqual(main.cmd_b(restored), 8)

    def test_peek_is_non_destructive_across_replays(self):
        state = self._full_state()
        self.assertEqual(main.cmd_g(state), 2)
        self.assertEqual(state["events"], {1: (5, 6), 2: (1, 2)})
        self.assertEqual(main.cmd_g(state), 2)

    def test_rollback_failed_load_leaves_state_untouched(self):
        state = self._full_state()
        state["src"] = 5
        before = copy.deepcopy(state)
        self.assertFalse(main.cmd_c(state))
        self.assertEqual(state, before)

    def test_rollback_pause_and_empty_car_do_not_mutate(self):
        state = self._full_state()
        state["closed"] = True
        before = copy.deepcopy(state)
        self.assertFalse(main.cmd_d(state))
        self.assertEqual(state, before)
        before = copy.deepcopy(state)
        self.assertFalse(main.cmd_f(state))
        self.assertEqual(state, before)

    def test_rollback_reset_clears_records_and_allows_clean_replay(self):
        state = self._full_state()
        self.assertTrue(main.cmd_h(state))
        self.assertEqual(state["records"], [])
        self.assertFalse(main.cmd_h(state))
        clean = self._full_state()
        clean["records"] = []
        self.assertTrue(main.cmd_i(clean))
        self.assertFalse(main.cmd_i(clean))

    def test_rollback_then_replay_queue_stays_fifo(self):
        state = self._full_state()
        self.assertEqual(main.cmd_j(state), 1)
        snapshot = copy.deepcopy(state)
        self.assertEqual(main.cmd_j(snapshot), 2)
        self.assertEqual(snapshot["queue"], [])

    def test_duplicate_request_and_single_run_flags_toggle_only_once(self):
        state = self._full_state()
        self.assertTrue(main.cmd_e(state))
        for _ in range(3):
            self.assertFalse(main.cmd_e(state))
        self.assertTrue(main.cmd_i(state))
        for _ in range(3):
            self.assertFalse(main.cmd_i(state))


if __name__ == "__main__":
    unittest.main()
