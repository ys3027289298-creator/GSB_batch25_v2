"""商船队交易系统：船舱、订单、港口三处状态互相影响。

设计原则：
- 每个 action 先校验、后落账，校验失败时不产生任何副作用；
- execute_trade 把"接单 -> 装船 -> 到港卸货 -> 结算入账"包成一笔
  原子交易：任何一步失败，金币、船舱、港口库存、流水整体回滚。
"""

import copy
import json


class TradeError(Exception):
    """交易失败：触发整体回滚。"""


STANDING_ORDER = "O1"


def new_game():
    return {
        "gold": 100,          # 金币
        "orders": [STANDING_ORDER],  # 已承接货单（开局常驻一单）
        "items": [],          # 船舱货物（先到先卸）
        "cap": 4,             # 船舱容量
        "slots": 0,           # 港口已用泊位
        "berths": 2,          # 港口泊位上限
        "stock": 0,           # 港口库存
        "count": 0,           # 成交笔数
        "amount": 0,          # 待结算金额
        "audit": [],          # 流水
        "paused": False,      # 暂停时不结算、不走钟
        "clock": 0,
        "seq": 2,             # 下一货单编号（存档续号，不跳号）
    }


def action_a(state):
    """承接货单：同一货单不能重复承接。"""
    orders = state.setdefault("orders", [])
    if STANDING_ORDER in orders:
        return False
    orders.append(STANDING_ORDER)
    return True


def action_b(state):
    """装货：船舱满了就拒装，不能再塞。"""
    if len(state["items"]) >= state["cap"]:
        return False
    state["items"].append("x")
    return True


def action_c(state):
    """结算：暂停期间不结算。"""
    if state.get("paused"):
        return False
    amount = state.get("amount", 0)
    state["gold"] = state.get("gold", 0) + amount
    state["count"] = state.get("count", 0) + 1
    state.setdefault("audit", []).append(("settle", amount))
    return True


def action_d(state):
    """成交计数：一笔交易只累计一次。"""
    state["count"] += 1
    return state["count"]


def action_e(state):
    """支付：空订单/余额不足整笔拒绝，不许扣成负数。"""
    cost = 5
    if state["amount"] < cost:
        return False
    state["amount"] -= cost
    return True


def action_f(state):
    """转运：源头扣多少，目的港就必须到账多少。"""
    if state["src"] < 5:
        return False
    state["src"] -= 5
    state["dst"] += 5
    return True


def action_g(state):
    """查看某船货单：返回筛选后的副本，绝不改动流水。"""
    return [row for row in state["audit"] if row[0] == "a"]


def action_h(state):
    """入港：泊位满了就拒绝靠港。"""
    if state["slots"] >= state["cap"]:
        return False
    state["slots"] += 1
    return True


def action_i(state):
    """重置：清空流水和经营状态，但保留货单序号，避免重置后重号。"""
    seq = state.get("seq", 1)
    state.clear()
    state.update(new_game())
    state["seq"] = seq
    return True


def action_j(state):
    """走钟：暂停时时钟不前进，编号不会跳过。"""
    if state.get("paused"):
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def issue_order(state):
    """开新货单：编号由 seq 发出，读档后连续不跳号。"""
    order_id = "O%d" % state["seq"]
    state["seq"] += 1
    state["orders"].append(order_id)
    return order_id


def save_game(state):
    return json.dumps(state)


def load_game(payload):
    """读档：序号以存档里的 seq 为准，不用 len(orders) 重算跳号。"""
    state = json.loads(payload)
    state.setdefault("seq", 1)
    return state


def _accept_order(state, order_id):
    if order_id in state["orders"]:
        raise TradeError("重复货单: %s" % order_id)
    state["orders"].append(order_id)


def _load_cargo(state, cargo):
    if len(state["items"]) + len(cargo) > state["cap"]:
        raise TradeError("船舱已满")
    state["items"].extend(cargo)


def _unload_at_port(state, cargo):
    if state["slots"] >= state["berths"]:
        raise TradeError("港口泊位已满")
    state["slots"] += 1
    for _ in cargo:
        state["items"].pop(0)  # 先到先卸
        state["stock"] += 1


def _settle(state, order_id, price):
    if state["paused"]:
        raise TradeError("已暂停，不能结算")
    state["gold"] += price
    state["count"] += 1
    state["audit"].append((order_id, price))


def execute_trade(state, order_id, cargo, price):
    """执行一笔完整交易；任一步失败则整体回滚，返回 False。"""
    snapshot = copy.deepcopy(state)
    try:
        _accept_order(state, order_id)
        _load_cargo(state, cargo)
        _unload_at_port(state, cargo)
        _settle(state, order_id, price)
    except TradeError:
        state.clear()
        state.update(snapshot)
        return False
    return True


def main():
    print("world 命令: run/quit")
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
