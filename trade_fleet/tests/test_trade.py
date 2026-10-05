import copy
import os
import tempfile
import unittest

import world


class TestTradeFleet(unittest.TestCase):
    def test_duplicate_order_rejected(self):
        state = world.new_game()
        self.assertFalse(world.accept_order(state, "ORD-1"))
        self.assertEqual(len(state["orders"]), 1)
        self.assertTrue(world.accept_order(state, "ORD-2"))

    def test_hold_full_rejects_loading(self):
        state = world.new_game()
        for _ in range(state["cap"]):
            self.assertTrue(world.load_cargo(state, "x"))
        self.assertFalse(world.load_cargo(state, "x"))
        self.assertEqual(len(state["items"]), state["cap"])

    def test_unload_is_fifo(self):
        state = world.new_game()
        world.load_cargo(state, "first")
        world.load_cargo(state, "second")
        self.assertEqual(world.unload_cargo(state), "first")
        self.assertEqual(world.unload_cargo(state), "second")
        self.assertIsNone(world.unload_cargo(state))

    def test_view_manifest_does_not_delete(self):
        state = world.new_game()
        state["audit"] = [("a", 1), ("b", 2), ("a", 3)]
        rows = world.view_manifest(state, "a")
        self.assertEqual(rows, [("a", 1), ("a", 3)])
        self.assertEqual(state["audit"], [("a", 1), ("b", 2), ("a", 3)])

    def test_settle_credits_gold_and_counts_once(self):
        state = world.new_game()
        world.load_cargo(state, "x")
        self.assertTrue(world.settle_orders(state))
        self.assertEqual(state["gold"], 105)
        self.assertEqual(state["count"], 1)
        self.assertEqual(state["audit"], [("a", 5)])
        self.assertEqual(state["orders"], [])

    def test_paused_blocks_settle_and_tick(self):
        state = world.new_game()
        state["paused"] = True
        self.assertFalse(world.settle_orders(state))
        self.assertEqual(world.tick(state), 0)
        self.assertEqual(state["gold"], 100)

    def test_reset_clears_ledger(self):
        state = world.new_game()
        state["audit"] = [("a", 5)]
        state["count"] = 3
        state["clock"] = 9
        world.reset_game(state)
        self.assertEqual(state["audit"], [])
        self.assertEqual(state["count"], 0)
        self.assertEqual(state["clock"], 0)

    def test_save_load_keeps_id_sequence(self):
        state = world.new_game()
        world.accept_order(state, "ORD-2")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            world.save_game(state, path)
            loaded = world.load_game(path)
        self.assertEqual(loaded["next_id"], state["next_id"])
        self.assertTrue(world.accept_order(loaded, "ORD-3"))
        self.assertEqual(loaded["next_id"], state["next_id"] + 1)

    def test_failed_trade_rolls_back_entirely(self):
        state = world.new_game()
        state.update({"src": 10, "dst": 0})
        for _ in range(state["cap"]):
            world.load_cargo(state, "x")
        before = copy.deepcopy(state)
        steps = [
            lambda s: world.transfer_gold(s, 5),
            lambda s: world.record_trade(s) and True,
            lambda s: world.load_cargo(s, "overflow"),
        ]
        self.assertFalse(world.execute_trade(state, steps))
        self.assertEqual(state, before)

    def test_failed_trade_rolls_back_on_exception(self):
        state = world.new_game()
        before = copy.deepcopy(state)

        def boom(s):
            s["gold"] -= 50
            raise RuntimeError("港口失联")

        self.assertFalse(world.execute_trade(state, [boom]))
        self.assertEqual(state, before)

    def test_successful_trade_commits(self):
        state = world.new_game()
        state.update({"src": 10, "dst": 0})
        steps = [
            lambda s: world.transfer_gold(s, 5),
            lambda s: world.load_cargo(s, "x"),
        ]
        self.assertTrue(world.execute_trade(state, steps))
        self.assertEqual(state["dst"], 5)
        self.assertEqual(state["items"], ["x"])


if __name__ == "__main__":
    unittest.main()
