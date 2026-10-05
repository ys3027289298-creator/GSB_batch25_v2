import json


def new_game():
    return {
        "ships": {},
        "pending_ship": 1,
        "fleet": [1, 2],
        "fleet_capacity": 2,
        "events": {},
        "queue": [],
        "items": [],
        "next_id": 1,
        "src": 0,
        "dst": 0,
        "closed": False,
        "position": 0,
        "target": 1,
        "paused": False,
        "hits": 0,
        "save": None,
    }


def action_a(state):
    # 新舰船入役：舷号已存在时拒绝，避免重复舰船。
    ship_id = state["pending_ship"]
    if ship_id in state["ships"]:
        return False
    state["ships"][ship_id] = {"id": ship_id, "sector": None}
    return True


def action_b(state):
    # 舰船编入舰队：舰队满载时拒绝编队。
    if len(state["fleet"]) >= state["fleet_capacity"]:
        return False
    state["fleet"].append(state["pending_ship"])
    return True


def action_c(state):
    # 侦察海域：返回敌情最轻（最空）的海域编号；无海域时返回 None 而非文本。
    if not state["events"]:
        return None
    return min(state["events"].items(), key=lambda item: item[1][0])[0]


def action_d(state):
    # 主炮攻击：只有率先抵达目标的舰船才能开火。
    if state["position"] < state["target"]:
        return False
    state["hits"] += 1
    return True


def action_e(state):
    # 舰队前进：暂停或已抵达目标时不得继续前进。
    if state["paused"] or state["position"] >= state["target"]:
        return False
    state["position"] += 1
    if state["position"] >= state["target"]:
        state["paused"] = True
    return True


def action_f(state):
    # 查看队首舰船：只查看，不从队列中误删。
    if not state["queue"]:
        return None
    return state["queue"][0]


def action_g(state):
    # 清点弹药：返回实际弹药基数，不少算。
    return len(state["items"])


def action_h(state):
    # 本轮战果结算：同一轮只累计一次，重复查询不重复累计。
    return state["next_id"]


def action_i(state):
    # 重置战局：清空战果统计，但保留舰队资源。
    state["dst"] = 0
    state["hits"] = 0
    return True


def action_j(state):
    # 读档：从存档槽恢复进度；存档已关闭则失败，恢复编号不跳号。
    if state["closed"]:
        return False
    if state["save"]:
        state.update(json.loads(state["save"]))
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
