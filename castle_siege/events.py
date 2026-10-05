import json


def new_game():
    return {
        "paused": False,
        "clock": 0,
        "count": 0,
        "amount": 0,
        "src": 0,
        "dst": 0,
        "audit": [],
        "slots": 0,
        "cap": 0,
        "items": [],
        "enemies": [],
        "casualties": 0,
        "next_id": 1,
    }


def event_a(state):
    # 开火：暂停时拒绝对外输出，状态不变
    if state.get("paused"):
        return False
    return True


def event_b(state):
    # 计箭：每轮只累计一次
    state["count"] += 1
    return state["count"]


def event_c(state):
    # 消耗：先校验后扣减，失败路径整体回滚（不产生负库存）
    if state["amount"] < 5:
        return False
    state["amount"] -= 5
    return True


def event_d(state):
    # 转运：转出与转入在同一轮提交，箭矢总数守恒
    if state["src"] < 5:
        return False
    state["src"] -= 5
    state["dst"] += 5
    return True


def event_e(state):
    # 查看审计：只读过滤，返回副本，绝不改动原列表
    return [row for row in state["audit"] if row[0] == "a"]


def event_f(state):
    # 登墙部署：城墙满员时拒绝，不占位
    if state["slots"] >= state["cap"]:
        return False
    state["slots"] += 1
    return True


def event_g(state):
    # 阵地是否空置：返回纯布尔，空阵地不返回文本
    return not state.get("enemies")


def event_h(state):
    # 时钟：暂停时冻结，不推进
    if state.get("paused"):
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def event_i(state):
    # 迎击：队列为空时拒绝；否则按到达顺序迎击最先来的敌人
    if not state.get("enemies"):
        return False
    return state["enemies"].pop(0)


def event_j(state):
    # 派遣攻城队：先校验（满员/重复）再入队，失败路径不入队
    if len(state["items"]) >= state["cap"]:
        return False
    if "x" in state["items"]:
        return False
    state["items"].append("x")
    return True


def reset(state):
    # 重置：伤亡等战斗结果一并清零
    state["casualties"] = 0
    state["count"] = 0
    state["clock"] = 0
    return state


def save_game(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    return True


def load_game(state, path):
    # 读档：整体替换为存档快照，编号计数器随档恢复，不跳号
    with open(path, "r", encoding="utf-8") as fh:
        snapshot = json.load(fh)
    state.clear()
    state.update(snapshot)
    return state


def next_id(state):
    # 编号从状态机内部分配，单调递增且随存档持久化
    assigned = state["next_id"]
    state["next_id"] += 1
    return assigned


def main():
    print("events 命令: run/quit")
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
