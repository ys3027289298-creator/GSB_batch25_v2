import copy
import json
import os
import tempfile
import unittest

import main


def make_state():
    state = main.new_game()
    state["compartments"]["engine"]["oxygen"] = 50
    state["compartments"]["bridge"]["oxygen"] = 50
    return state


class TestFaultIntake(unittest.TestCase):
    def test_duplicate_fault_rejected(self):
        state = make_state()
        first = main.report_fault(state, "engine", "leak")
        self.assertIsNotNone(first)
        self.assertIsNone(main.report_fault(state, "engine", "leak"))
        self.assertEqual(len(state["faults"]), 1)
        # 不同类型或不同舱室不受影响
        self.assertIsNotNone(main.report_fault(state, "engine", "pump"))
        self.assertIsNotNone(main.report_fault(state, "bridge", "leak"))
        self.assertEqual(len(state["faults"]), 3)

    def test_over_capacity_rejected(self):
        state = make_state()
        for idx in range(main.MAX_FAULTS_PER_COMPARTMENT):
            self.assertIsNotNone(main.report_fault(state, "engine", "f%d" % idx))
        self.assertIsNone(main.report_fault(state, "engine", "overflow"))
        self.assertEqual(len(state["faults"]), main.MAX_FAULTS_PER_COMPARTMENT)
        # 其它舱室仍可接收
        self.assertIsNotNone(main.report_fault(state, "bridge", "ok"))

    def test_report_to_unknown_compartment(self):
        state = make_state()
        self.assertIsNone(main.report_fault(state, "nowhere", "leak"))
        self.assertEqual(state["faults"], [])


class TestCompartmentInspection(unittest.TestCase):
    def test_empty_compartment_returns_none_not_placeholder(self):
        state = make_state()
        self.assertIsNone(main.inspect_compartment(state, "void"))
        self.assertNotEqual(main.inspect_compartment(state, "void"), "empty")
        self.assertIsNotNone(main.inspect_compartment(state, "engine"))


class TestFaultQueue(unittest.TestCase):
    def test_first_in_fault_prioritized(self):
        state = make_state()
        t1 = main.report_fault(state, "engine", "leak")
        t2 = main.report_fault(state, "bridge", "sonar")
        self.assertEqual(main.peek_next_fault(state)["id"], t1["id"])
        self.assertTrue(main.repair(state))
        self.assertEqual(state["repair_log"][0]["ticket_id"], t1["id"])
        self.assertEqual(main.peek_next_fault(state)["id"], t2["id"])

    def test_view_fault_does_not_delete(self):
        state = make_state()
        ticket = main.report_fault(state, "engine", "leak")
        seen = main.view_fault(state, ticket["id"])
        self.assertEqual(seen["type"], "leak")
        self.assertEqual(len(state["faults"]), 1)
        self.assertIsNone(main.view_fault(state, 999))
        self.assertEqual(len(state["faults"]), 1)


class TestDoorLock(unittest.TestCase):
    def test_locked_door_blocks_repair(self):
        state = make_state()
        main.report_fault(state, "engine", "leak")
        main.lock_door(state, "engine", True)
        self.assertFalse(main.repair(state))
        self.assertEqual(len(state["faults"]), 1)
        self.assertEqual(state["repair_log"], [])
        main.lock_door(state, "engine", False)
        self.assertTrue(main.repair(state))
        self.assertEqual(len(state["repair_log"]), 1)


class TestSpares(unittest.TestCase):
    def test_spare_capacity_not_off_by_one(self):
        state = make_state()
        state["spares"] = {"used": 1, "cap": 2}
        self.assertEqual(main.spare_capacity(state), 1)
        # 仅剩一件时仍可维修
        main.report_fault(state, "engine", "leak")
        self.assertTrue(main.repair(state))
        self.assertEqual(main.spare_capacity(state), 0)

    def test_no_spares_blocks_repair(self):
        state = make_state()
        state["spares"] = {"used": 2, "cap": 2}
        main.report_fault(state, "engine", "leak")
        self.assertFalse(main.repair(state))
        self.assertEqual(len(state["faults"]), 1)


class TestRepairAccounting(unittest.TestCase):
    def test_single_repair_counted_once(self):
        state = make_state()
        ticket = main.report_fault(state, "engine", "leak")
        self.assertTrue(main.repair(state, ticket["id"]))
        self.assertEqual(len(state["repair_log"]), 1)
        self.assertEqual(state["spares"]["used"], 1)
        self.assertEqual(state["compartments"]["engine"]["oxygen"], 40)
        self.assertEqual(state["ballast"], main.BALLAST_PER_REPAIR)
        # 同一单重复维修是幂等的，不会重复累计
        self.assertFalse(main.repair(state, ticket["id"]))
        self.assertEqual(len(state["repair_log"]), 1)
        self.assertEqual(state["spares"]["used"], 1)

    def test_repair_missing_ticket(self):
        state = make_state()
        self.assertFalse(main.repair(state, 999))
        self.assertEqual(state["repair_log"], [])


class TestReset(unittest.TestCase):
    def test_reset_clears_log_and_faults(self):
        state = make_state()
        main.report_fault(state, "engine", "leak")
        main.report_fault(state, "bridge", "sonar")
        main.repair(state)
        main.lock_door(state, "bridge", True)
        self.assertEqual(len(state["repair_log"]), 1)
        main.reset(state)
        self.assertEqual(state["repair_log"], [])
        self.assertEqual(state["faults"], [])
        self.assertEqual(state["ballast"], 0)
        self.assertEqual(state["spares"]["used"], 0)
        self.assertEqual(state["next_ticket_id"], 1)
        self.assertFalse(state["compartments"]["bridge"]["locked"])


class TestSaveLoad(unittest.TestCase):
    def test_load_keeps_ticket_numbering_continuous(self):
        state = make_state()
        t1 = main.report_fault(state, "engine", "leak")
        main.repair(state, t1["id"])
        t2 = main.report_fault(state, "bridge", "sonar")
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            main.save_game(state, path)
            # 模拟旧存档：票据计数器缺失，读档后不得跳号/撞号
            with open(path, encoding="utf-8") as fh:
                raw = json.load(fh)
            del raw["next_ticket_id"]
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(raw, fh)
            loaded = main.new_game()
            main.load_game(loaded, path)
        self.assertEqual(loaded["next_ticket_id"], t2["id"] + 1)
        t3 = main.report_fault(loaded, "engine", "pump")
        self.assertEqual(t3["id"], t2["id"] + 1)
        ids = [t["id"] for t in loaded["faults"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_save_load_roundtrip(self):
        state = make_state()
        main.report_fault(state, "engine", "leak")
        main.repair(state)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "save.json")
            main.save_game(state, path)
            loaded = main.new_game()
            main.load_game(loaded, path)
        self.assertEqual(loaded, state)


class TestRollbackReplay(unittest.TestCase):
    def test_failed_repair_rolls_back_and_replays(self):
        state = make_state()
        main.report_fault(state, "engine", "leak")
        # 压载逼近上限：维修会因压载超限而失败
        state["ballast"] = main.BALLAST_LIMIT
        before = copy.deepcopy(state)
        self.assertFalse(main.repair(state))
        # 回滚后状态与操作前完全一致（氧气/备件/压载/故障单/日志均未污染）
        self.assertEqual(state, before)
        # 排除故障诱因后，同一状态可重放并成功
        state["ballast"] = 0
        self.assertTrue(main.repair(state))
        self.assertEqual(len(state["repair_log"]), 1)
        self.assertEqual(state["spares"]["used"], 1)
        self.assertEqual(state["compartments"]["engine"]["oxygen"], 40)

    def test_rollback_on_unexpected_error_mid_transaction(self):
        state = make_state()
        main.report_fault(state, "engine", "leak")
        # 人为制造事务中途的意外异常（氧气账本损坏）
        state["compartments"]["engine"]["oxygen"] = "corrupted"
        before = copy.deepcopy(state)
        self.assertFalse(main.repair(state))
        self.assertEqual(state, before)
        # 修复账本后重放成功
        state["compartments"]["engine"]["oxygen"] = 50
        self.assertTrue(main.repair(state))

    def test_failed_sequence_replays_identically(self):
        # 一段含失败操作的指令序列，重放两次结果必须一致
        def run_script():
            state = make_state()
            main.report_fault(state, "engine", "leak")
            main.report_fault(state, "bridge", "sonar")
            main.lock_door(state, "engine", True)
            main.repair(state, 1)          # 锁定失败 -> 回滚
            main.repair(state)             # FIFO 仍是 1 号，仍失败
            main.lock_door(state, "engine", False)
            main.repair(state)             # 现在成功修 1 号
            main.repair(state, 1)          # 幂等拒绝
            main.repair(state)             # 修 2 号
            return state

        first = run_script()
        second = run_script()
        self.assertEqual(first, second)
        self.assertEqual([e["ticket_id"] for e in first["repair_log"]], [1, 2])
        self.assertEqual(first["spares"]["used"], 2)


if __name__ == "__main__":
    unittest.main()
