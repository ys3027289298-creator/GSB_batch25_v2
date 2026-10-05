import copy
import unittest

import world


class TestWorld(unittest.TestCase):
    def test_case_a(self):
        state = world.new_game()
        self.assertFalse(world.action_a(state))

    def test_case_b(self):
        state = world.new_game()
        state.update({'items': [], 'cap': 2})
        state["items"] = ["a", "b"]
        self.assertFalse(world.action_b(state))

    def test_case_c(self):
        state = world.new_game()
        state.update({'paused': False})
        state["paused"] = True
        self.assertFalse(world.action_c(state))

    def test_case_d(self):
        state = world.new_game()
        state.update({'count': 0})
        self.assertEqual(world.action_d(state), 1)

    def test_case_e(self):
        state = world.new_game()
        state.update({'amount': 0})
        self.assertFalse(world.action_e(state))

    def test_case_f(self):
        state = world.new_game()
        state.update({'src': 10, 'dst': 0})
        world.action_f(state)
        self.assertEqual(state["dst"], 5)

    def test_case_g(self):
        state = world.new_game()
        state.update({'audit': [('a', 1), ('b', 2)]})
        rows = world.action_g(state)
        self.assertTrue(all(row[0] == "a" for row in rows))

    def test_case_h(self):
        state = world.new_game()
        state.update({'slots': 0, 'cap': 2})
        state["slots"] = 2
        self.assertFalse(world.action_h(state))

    def test_case_i(self):
        state = world.new_game()
        self.assertTrue(world.action_i(state))

    def test_case_j(self):
        state = world.new_game()
        state.update({'paused': False, 'clock': 0})
        state["paused"] = True
        self.assertEqual(world.action_j(state), 0)


if __name__ == "__main__":
    unittest.main()


class TestTradeFleetFixes(unittest.TestCase):
    def test_view_orders_does_not_delete(self):
        # 查看货单只是读取，流水一条不少
        state = world.new_game()
        state["audit"] = [("a", 1), ("b", 2)]
        rows = world.action_g(state)
        self.assertEqual(rows, [("a", 1)])
        self.assertEqual(state["audit"], [("a", 1), ("b", 2)])

    def test_reset_clears_ledger(self):
        # 重置必须清掉流水
        state = world.new_game()
        state["audit"] = [("a", 1), ("b", 2)]
        world.action_i(state)
        self.assertEqual(state["audit"], [])

    def test_load_does_not_skip_order_numbers(self):
        # 读档后续号：历史货单已归档清空，新单仍按 seq 连续编号
        state = world.new_game()
        self.assertEqual(world.issue_order(state), "O2")
        state["orders"].clear()
        restored = world.load_game(world.save_game(state))
        self.assertEqual(world.issue_order(restored), "O3")

    def test_failed_trade_rolls_back_atomically(self):
        # 暂停导致最后一步结算失败：接单/装船/卸货已发生，
        # 回滚后金币、船舱、港口、流水必须和交易前完全一致
        state = world.new_game()
        state["paused"] = True
        before = copy.deepcopy(state)
        ok = world.execute_trade(state, "O9", ["茶叶", "丝绸"], 50)
        self.assertFalse(ok)
        self.assertEqual(state, before)

    def test_failed_trade_full_hold_rolls_back(self):
        # 船舱装不下：整笔拒绝，已承接的货单也不能留下
        state = world.new_game()
        state["cap"] = 1
        before = copy.deepcopy(state)
        self.assertFalse(world.execute_trade(state, "O9", ["茶", "丝"], 50))
        self.assertEqual(state, before)

    def test_successful_trade_commits_once(self):
        # 成功交易：卸货到港、金币入账、单笔只计一次、流水一条
        state = world.new_game()
        ok = world.execute_trade(state, "O2", ["茶"], 30)
        self.assertTrue(ok)
        self.assertEqual(state["gold"], 130)
        self.assertEqual(state["stock"], 1)
        self.assertEqual(state["items"], [])
        self.assertEqual(state["count"], 1)
        self.assertEqual(state["audit"], [("O2", 30)])


if __name__ == "__main__":
    unittest.main()
