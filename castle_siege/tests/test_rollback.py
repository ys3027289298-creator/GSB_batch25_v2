import copy
import os
import tempfile
import unittest

import events


class TestRollback(unittest.TestCase):
    """每个事件的失败路径都必须保持状态不变（先校验、后提交）。"""

    def assert_rolled_back(self, state, event):
        before = copy.deepcopy(state)
        result = event(state)
        self.assertFalse(result)
        self.assertEqual(state, before)

    def test_fire_rejected_while_paused(self):
        self.assert_rolled_back({"paused": True}, events.event_a)

    def test_consume_rejected_when_insufficient(self):
        self.assert_rolled_back({"amount": 3}, events.event_c)

    def test_transfer_rejected_when_insufficient(self):
        self.assert_rolled_back({"src": 2, "dst": 7}, events.event_d)

    def test_deploy_rejected_when_wall_full(self):
        self.assert_rolled_back({"slots": 2, "cap": 2}, events.event_f)

    def test_intercept_rejected_when_no_enemy(self):
        self.assert_rolled_back({"enemies": []}, events.event_i)

    def test_dispatch_rejected_when_full(self):
        self.assert_rolled_back({"items": ["a", "b"], "cap": 2}, events.event_j)

    def test_dispatch_rejected_when_duplicate(self):
        self.assert_rolled_back({"items": ["x"], "cap": 3}, events.event_j)

    def test_clock_frozen_while_paused(self):
        state = {"paused": True, "clock": 4}
        self.assertEqual(events.event_h(state), 4)
        self.assertEqual(state["clock"], 4)

    def test_view_does_not_mutate_audit(self):
        state = {"audit": [("a", 1), ("b", 2)]}
        rows = events.event_e(state)
        self.assertEqual(rows, [("a", 1)])
        self.assertEqual(state["audit"], [("a", 1), ("b", 2)])

    def test_intercept_takes_first_arrival(self):
        state = {"enemies": ["orc", "troll"]}
        self.assertEqual(events.event_i(state), "orc")
        self.assertEqual(state["enemies"], ["troll"])

    def test_reset_clears_casualties(self):
        state = events.new_game()
        state["casualties"] = 9
        events.reset(state)
        self.assertEqual(state["casualties"], 0)

    def test_load_does_not_skip_ids(self):
        state = events.new_game()
        first = events.next_id(state)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            events.save_game(state, path)
            events.next_id(state)
            events.load_game(state, path)
        self.assertEqual(events.next_id(state), first + 1)


if __name__ == "__main__":
    unittest.main()
