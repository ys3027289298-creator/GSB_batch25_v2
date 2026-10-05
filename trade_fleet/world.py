import copy
import json


class TradeError(Exception):
    """交易失败, 触发整体回滚."""


def new_game():
    return {
        "gold": 100,
        "items": [],
        "cap": 4,
        "orders": [{"id": "ORD-1", "port": "a", "cargo": "x", "price": 5}],
        "audit": [],
        "slots": 0,
        "count": 0,
        "clock": 0,
        "paused": False,
        "next_id": 2,
    }


def accept_order(state, order_id="ORD-1", port="a", cargo="x", price=5):
    orders = state.setdefault("orders", [])
    if any(order["id"] == order_id for order in orders):
        return False
    orders.append({"id": order_id, "port": port, "cargo": cargo, "price": price})
    state["next_id"] = state.get("next_id", 1) + 1
    return True


def load_cargo(state, cargo="x"):
    if len(state["items"]) >= state["cap"]:
        return False
    state["items"].append(cargo)
    return True


def unload_cargo(state):
    if not state["items"]:
        return None
    return state["items"].pop(0)


def dock(state):
    if state["slots"] >= state["cap"]:
        return False
    state["slots"] += 1
    return True


def settle_orders(state):
    if state.get("paused"):
        return False
    remaining = []
    for order in state.get("orders", []):
        if order["cargo"] in state["items"]:
            state["items"].remove(order["cargo"])
            state["gold"] = state.get("gold", 0) + order["price"]
            state["audit"].append((order["port"], order["price"]))
            state["count"] += 1
        else:
            remaining.append(order)
    state["orders"] = remaining
    return True


def record_trade(state):
    state["count"] += 1
    return state["count"]


def pay(state, amount=5):
    if state["amount"] < amount:
        return False
    state["amount"] -= amount
    return True


def transfer_gold(state, amount=5):
    if state["src"] < amount:
        return False
    state["src"] -= amount
    state["dst"] += amount
    return True


def view_manifest(state, port="a"):
    return [row for row in state["audit"] if row[0] == port]


def reset_game(state):
    state["audit"] = []
    state["count"] = 0
    state["clock"] = 0
    state["slots"] = 0
    state["paused"] = False
    return True


def tick(state):
    if state.get("paused"):
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def save_game(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False)
    return True


def load_game(path):
    with open(path, "r", encoding="utf-8") as fh:
        state = json.load(fh)
    state["audit"] = [tuple(row) for row in state.get("audit", [])]
    return state


def execute_trade(state, steps):
    """原子执行一组交易步骤: 任一步失败或抛错, 状态整体回滚."""
    snapshot = copy.deepcopy(state)
    try:
        for step in steps:
            if step(state) is False:
                raise TradeError("交易步骤被拒绝")
    except Exception:
        state.clear()
        state.update(snapshot)
        return False
    return True


def action_a(state):
    return accept_order(state, "ORD-1")


def action_b(state):
    return load_cargo(state, "x")


def action_c(state):
    return settle_orders(state)


def action_d(state):
    return record_trade(state)


def action_e(state):
    return pay(state, 5)


def action_f(state):
    return transfer_gold(state, 5)


def action_g(state):
    return view_manifest(state, "a")


def action_h(state):
    return dock(state)


def action_i(state):
    return reset_game(state)


def action_j(state):
    return tick(state)


def main():
    state = new_game()
    print("trade_fleet 命令: orders/load/unload/settle/manifest/reset/tick/quit")
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw or raw == "quit":
            break
        if raw == "orders":
            print(state["orders"])
        elif raw == "load":
            print("ok" if load_cargo(state) else "船舱已满")
        elif raw == "unload":
            cargo = unload_cargo(state)
            print(cargo if cargo is not None else "船舱为空")
        elif raw == "settle":
            print("ok" if settle_orders(state) else "已暂停, 无法结算")
        elif raw == "manifest":
            print(view_manifest(state))
        elif raw == "reset":
            reset_game(state)
            print("ok")
        elif raw == "tick":
            print(tick(state))
        else:
            print("未知命令")


if __name__ == "__main__":
    main()
