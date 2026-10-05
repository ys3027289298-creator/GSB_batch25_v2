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

    def test_transfer_boundary(self):
        state = main.new_game()
        state.update({'src': 10, 'dst': 0})
        self.assertTrue(main.cmd_c(state))
        self.assertEqual(state["src"], 0)
        self.assertEqual(state["dst"], 10)
        self.assertFalse(main.cmd_c(state))
        self.assertEqual(state["src"], 0)
        self.assertEqual(state["dst"], 10)

    def test_rollback_clears_records(self):
        state = main.new_game()
        state.update({'events': {}})
        self.assertTrue(main.cmd_e(state))
        self.assertFalse(main.cmd_e(state))
        self.assertTrue(main.cmd_i(state))
        self.assertFalse(main.cmd_i(state))
        fresh = main.new_game()
        fresh.update({'events': {}})
        self.assertTrue(main.cmd_e(fresh))
        self.assertTrue(main.cmd_i(fresh))
        self.assertFalse(main.cmd_f(fresh))
        self.assertFalse(main.cmd_h(fresh))

    def test_replay_same_sequence_same_result(self):
        def run():
            s = main.new_game()
            s.update({'items': [1, 2], 'next_id': 7, 'src': 25, 'dst': 0,
                      'closed': False, 'events': {}, 'queue': [1, 2]})
            log = []
            log.append(main.cmd_a(s))
            log.append(main.cmd_b(s))
            log.append(main.cmd_b(s))
            log.append(main.cmd_c(s))
            log.append(main.cmd_c(s))
            log.append(main.cmd_c(s))
            log.append(main.cmd_d(s))
            log.append(main.cmd_e(s))
            log.append(main.cmd_e(s))
            log.append(main.cmd_h(s))
            log.append(main.cmd_j(s))
            log.append(main.cmd_j(s))
            log.append(main.cmd_i(s))
            log.append(main.cmd_i(s))
            return log, s

        log1, state1 = run()
        log2, state2 = run()
        self.assertEqual(log1, log2)
        self.assertEqual(state1, state2)
        self.assertEqual(log1, [2, 7, 8, True, True, False, True,
                                True, False, 1, 1, 2, True, False])
        self.assertEqual(state1["next_id"], 9)
        self.assertEqual(state1["src"], 5)
        self.assertEqual(state1["dst"], 20)
        self.assertEqual(state1["queue"], [])


if __name__ == "__main__":
    unittest.main()
