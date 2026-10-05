"""潜艇维修游戏核心模块。

状态由四个子系统共同维护，边界操作必须互相隔离：
- 隔离舱 (compartments): 每舱有氧气与舱门锁
- 压载舱 (ballast): 维修会调整压载，超限时整单回滚
- 备件库 (spares): used/cap 计量，余量 = cap - used
- 维修日志 (repair_log): 每次成功维修恰好追加一条
"""

import copy
import json

MAX_FAULTS_PER_COMPARTMENT = 4
OXYGEN_PER_REPAIR = 10
BALLAST_PER_REPAIR = 5
BALLAST_LIMIT = 100
DEFAULT_COMPARTMENT_OXYGEN = 50


class _RepairError(Exception):
    """维修事务内部失败，触发状态回滚。"""


def new_game():
    state = {
        "compartments": {},
        "faults": [],
        "spares": {"used": 0, "cap": 20},
        "ballast": 0,
        "repair_log": [],
        "next_ticket_id": 1,
    }
    for name in ("engine", "bridge", "cargo"):
        add_compartment(state, name)
    return state


def add_compartment(state, name, oxygen=DEFAULT_COMPARTMENT_OXYGEN):
    state["compartments"][name] = {"oxygen": oxygen, "locked": False}
    return True


def report_fault(state, compartment, fault_type):
    comp = state["compartments"].get(compartment)
    if comp is None:
        return None
    # 同一舱室同类型故障单去重
    for ticket in state["faults"]:
        if ticket["compartment"] == compartment and ticket["type"] == fault_type:
            return None
    # 单舱故障单容量上限，超容量拒绝接收
    open_count = sum(1 for ticket in state["faults"] if ticket["compartment"] == compartment)
    if open_count >= MAX_FAULTS_PER_COMPARTMENT:
        return None
    ticket = {
        "id": state["next_ticket_id"],
        "compartment": compartment,
        "type": fault_type,
    }
    state["next_ticket_id"] += 1
    state["faults"].append(ticket)
    return ticket


def inspect_compartment(state, name):
    # 空舱室返回 None，而不是占位文本
    return state["compartments"].get(name)


def view_fault(state, ticket_id):
    # 只读查看，不得误删故障单
    for ticket in state["faults"]:
        if ticket["id"] == ticket_id:
            return ticket
    return None


def peek_next_fault(state):
    # 先入故障优先（FIFO），只窥视不弹出
    if not state["faults"]:
        return None
    return state["faults"][0]


def lock_door(state, name, locked=True):
    comp = state["compartments"].get(name)
    if comp is None:
        return False
    comp["locked"] = locked
    return True


def spare_capacity(state):
    # 备件余量 = cap - used，不少算一件
    return state["spares"]["cap"] - state["spares"]["used"]


def repair(state, ticket_id=None):
    """维修一张故障单（默认按 FIFO 取最早的未修故障）。

    整个操作是一个事务：任一子系统校验失败都会回滚全部已做的
    改动（氧气/备件/压载/故障单/日志），保证失败后可原样重放。
    """
    if ticket_id is None:
        if not state["faults"]:
            return False
        ticket_id = state["faults"][0]["id"]
    # 幂等：同一张单不会被重复累计
    if any(entry["ticket_id"] == ticket_id for entry in state["repair_log"]):
        return False
    snapshot = copy.deepcopy(state)
    try:
        ticket = next(
            (t for t in state["faults"] if t["id"] == ticket_id), None
        )
        if ticket is None:
            raise _RepairError("ticket not found")
        comp = state["compartments"].get(ticket["compartment"])
        if comp is None:
            raise _RepairError("compartment missing")
        if comp["locked"]:
            raise _RepairError("door locked")
        if comp["oxygen"] < OXYGEN_PER_REPAIR:
            raise _RepairError("insufficient oxygen")
        if spare_capacity(state) < 1:
            raise _RepairError("no spare parts")
        if state["ballast"] + BALLAST_PER_REPAIR > BALLAST_LIMIT:
            raise _RepairError("ballast limit exceeded")
        # 通过全部校验后才落账：氧气、备件、压载、故障单、日志各动一次
        comp["oxygen"] -= OXYGEN_PER_REPAIR
        state["spares"]["used"] += 1
        state["ballast"] += BALLAST_PER_REPAIR
        state["faults"].remove(ticket)
        state["repair_log"].append(
            {
                "ticket_id": ticket["id"],
                "compartment": ticket["compartment"],
                "type": ticket["type"],
            }
        )
    except Exception:
        # 失败回滚：状态恢复到操作前，之后可以安全重放
        state.clear()
        state.update(snapshot)
        return False
    return True


def reset(state):
    # 重置必须清空故障单与维修日志，并恢复各子系统初始值
    state["faults"] = []
    state["repair_log"] = []
    state["ballast"] = 0
    state["spares"] = {"used": 0, "cap": state["spares"]["cap"]}
    state["next_ticket_id"] = 1
    for comp in state["compartments"].values():
        comp["oxygen"] = DEFAULT_COMPARTMENT_OXYGEN
        comp["locked"] = False
    return True


def save_game(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    return True


def load_game(state, path):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    state.clear()
    state.update(data)
    # 读档后票据号必须连续：旧存档若缺/错了 next_ticket_id，
    # 依据现存故障单与维修日志中的最大票号校正，避免跳号或撞号
    used_ids = [t["id"] for t in state["faults"]]
    used_ids += [entry["ticket_id"] for entry in state["repair_log"]]
    expected = (max(used_ids) + 1) if used_ids else 1
    if state.get("next_ticket_id") != expected:
        state["next_ticket_id"] = expected
    return True


def main():
    print("main 命令: run/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        print("ok")


if __name__ == "__main__":
    main()
