import json


def new_game():
    """创建：推进、暂停、读档共享的同一份初始状态。"""
    return {
        "paused": False,
        "clock": 0,
        "cap": 2,
        "items": [],
        "slots": 0,
        "queue": [],
        "count": 0,
        "amount": 10,
        "src": 10,
        "dst": 0,
        "audit": [],
        "saves": {},
        "save_seq": 0,
    }

def rule_a(state):
    """重置：清空全部运行数据，包括操作记录与存档。"""
    fresh = new_game()
    state.clear()
    state.update(fresh)
    return True

def rule_b(state):
    """推进：暂停时风车停转，时钟不走。"""
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]

def rule_c(state):
    """执行：先入先出执行队首任务，空队列返回 False。"""
    if not state["queue"]:
        return False
    task = state["queue"].pop(0)
    state["audit"].append(("run", task))
    return task

def rule_d(state):
    """分配任务：满负荷或重复分配时拒绝。"""
    if len(state["items"]) >= state["cap"] or "x" in state["items"]:
        return False
    state["items"].append("x")
    return True

def rule_e(state):
    """转动：暂停时风车停转。"""
    return not state["paused"]

def rule_f(state):
    """调度：单次调度只累计一次。"""
    state["count"] += 1
    return state["count"]

def rule_g(state):
    """配电：余额不足时拒绝，不做超额扣减。"""
    if state["amount"] < 5:
        return False
    state["amount"] -= 5
    return True

def rule_h(state):
    """输电：电站扣多少，风车就入账多少。"""
    state["src"] -= 5
    state["dst"] += 5
    return True

def rule_i(state):
    """查看：只读过滤记录，不删除任何条目。"""
    return [row for row in state["audit"] if row[0] == "a"]

def rule_j(state):
    """叶片：槽位占满后不再接收。"""
    if state["slots"] >= state["cap"]:
        return False
    state["slots"] += 1
    return True

def save_game(state):
    """存档：返回连续编号，读档后编号仍连续。"""
    state["save_seq"] += 1
    slot = state["save_seq"]
    snapshot = {k: v for k, v in state.items() if k not in ("saves", "save_seq")}
    state["saves"][slot] = json.loads(json.dumps(snapshot))
    return slot

def load_game(state, slot):
    """读档：按编号精确恢复，不跳号、不推进存档序号。"""
    if slot not in state["saves"]:
        return False
    saves = state["saves"]
    save_seq = state["save_seq"]
    snapshot = json.loads(json.dumps(state["saves"][slot]))
    state.clear()
    state.update(snapshot)
    state["saves"] = saves
    state["save_seq"] = save_seq
    return True

def main():
    print("windmill_island 命令: new/tick/pause/resume/add/queue/run/slot/"
          "spin/dispatch/alloc/transfer/view/save/load/reset/status/quit")
    state = new_game()
    while True:
        try:
            raw = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not raw:
            continue
        if raw == "quit":
            break
        parts = raw.split()
        cmd = parts[0]
        arg = parts[1] if len(parts) > 1 else None
        if cmd == "new":
            state = new_game()
            print("ok 已创建新游戏")
        elif cmd == "tick":
            print("clock =", rule_b(state))
        elif cmd == "pause":
            state["paused"] = True
            print("ok 已暂停")
        elif cmd == "resume":
            state["paused"] = False
            print("ok 已恢复")
        elif cmd == "add":
            task = arg or "x"
            if len(state["items"]) >= state["cap"] or task in state["items"]:
                print("拒绝: 满负荷或重复分配")
            else:
                state["items"].append(task)
                print("ok 已分配", task)
        elif cmd == "queue":
            task = arg or "x"
            state["queue"].append(task)
            print("ok 已入队", task)
        elif cmd == "run":
            result = rule_c(state)
            if result is False:
                print("空队列: 无任务可执行")
            else:
                print("ok 执行", result)
        elif cmd == "slot":
            print("ok 叶片就位" if rule_j(state) else "拒绝: 叶片槽已满")
        elif cmd == "spin":
            print("ok 风车转动" if rule_e(state) else "暂停中: 风车停转")
        elif cmd == "dispatch":
            print("dispatch =", rule_f(state))
        elif cmd == "alloc":
            print("ok 已配电" if rule_g(state) else "拒绝: 电量不足")
        elif cmd == "transfer":
            rule_h(state)
            print("ok src =", state["src"], "dst =", state["dst"])
        elif cmd == "view":
            kind = arg or "run"
            print("记录:", [row for row in state["audit"] if row[0] == kind])
        elif cmd == "save":
            print("ok 存档编号", save_game(state))
        elif cmd == "load":
            slot = int(arg) if arg else 0
            print("ok 已读档" if load_game(state, slot) else "拒绝: 存档不存在")
        elif cmd == "reset":
            rule_a(state)
            print("ok 已重置")
        elif cmd == "status":
            print(json.dumps(state, ensure_ascii=False))
        else:
            print("未知命令:", cmd)

if __name__ == "__main__":
    main()
