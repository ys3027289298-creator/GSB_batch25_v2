import unittest

import core


class TestCore(unittest.TestCase):
    def test_duplicate_tome_rejected(self):
        state = core.new_game()
        first = core.receive_tome(state, "龙语魔法")
        self.assertIsNone(core.receive_tome(state, "龙语魔法"))
        self.assertEqual(len(state["tomes"]), 1)
        self.assertEqual(state["arrival_queue"], [first])

    def test_full_shelf_rejects_archive(self):
        state = core.new_game()
        for i in range(state["capacity"]):
            core.receive_tome(state, "卷%d" % i)
            core.archive_next(state, "东架")
        extra = core.receive_tome(state, "溢出卷")
        self.assertIsNone(core.archive_next(state, "东架"))
        self.assertEqual(state["arrival_queue"], [extra])
        self.assertEqual(len(state["shelves"]["东架"]), state["capacity"])

    def test_empty_shelf_returns_none(self):
        state = core.new_game()
        self.assertIsNone(core.view_shelf(state, "空架"))
        core.receive_tome(state, "卷")
        core.archive_next(state, "架")
        core.retrieve(state, "架")
        self.assertIsNone(core.view_shelf(state, "架"))

    def test_first_arrived_archived_first(self):
        state = core.new_game()
        first = core.receive_tome(state, "甲")
        second = core.receive_tome(state, "乙")
        self.assertEqual(core.archive_next(state, "架"), first)
        self.assertEqual(core.archive_next(state, "架"), second)
        self.assertEqual(state["archive"], [first, second])

    def test_paused_blocks_retrieve(self):
        state = core.new_game()
        core.receive_tome(state, "卷")
        core.archive_next(state, "架")
        core.pause(state)
        self.assertIsNone(core.retrieve(state, "架"))
        self.assertEqual(state["retrievals"], 0)
        self.assertEqual(state["candles"], core.START_CANDLES)
        core.resume(state)
        self.assertIsNotNone(core.retrieve(state, "架"))

    def test_view_tome_does_not_delete(self):
        state = core.new_game()
        tome_id = core.receive_tome(state, "卷")
        core.archive_next(state, "架")
        self.assertEqual(core.view_tome(state, tome_id)["title"], "卷")
        self.assertIn(tome_id, state["tomes"])
        self.assertIn(tome_id, state["shelves"]["架"])

    def test_retrieve_counts_candle_and_retrieval_once(self):
        state = core.new_game()
        core.receive_tome(state, "卷")
        core.archive_next(state, "架")
        core.retrieve(state, "架")
        self.assertEqual(state["candles"], core.START_CANDLES - core.RETRIEVE_COST)
        self.assertEqual(state["retrievals"], 1)

    def test_reset_clears_state(self):
        state = core.new_game()
        core.receive_tome(state, "卷")
        core.archive_next(state, "架")
        core.retrieve(state, "架")
        core.reset(state)
        self.assertEqual(state, core.new_game())

    def test_save_load_roundtrip(self):
        state = core.new_game()
        core.receive_tome(state, "甲")
        core.receive_tome(state, "乙")
        core.archive_next(state, "架")
        core.retrieve(state, "架")
        loaded = core.load(core.save(state))
        self.assertEqual(loaded, state)

    def test_load_preserves_next_id(self):
        state = core.new_game()
        core.receive_tome(state, "甲")
        core.receive_tome(state, "乙")
        loaded = core.load(core.save(state))
        tome_id = core.receive_tome(loaded, "丙")
        self.assertEqual(tome_id, "tome-3")
        self.assertEqual(len(loaded["tomes"]), 3)


if __name__ == "__main__":
    unittest.main()
