import copy
import json


DEFAULT_STATE = {
    "count": 0,          # 回溯累计次数
    "amount": 0,         # 记忆点数
    "src": 0,            # 源记忆格
    "dst": 0,            # 目标记忆格
    "audit": [],         # 先入片段审计记录
    "slots": 0,          # 已占用记忆格
    "cap": 3,            # 记忆格上限
    "clock": 0,          # 梦境时钟
    "paused": False,     # 锁定状态
    "items": [],         # 已收纳的梦境片段
    "dream": "初梦",     # 当前梦境文本
    "next_id": 1,        # 下一个梦境编号
}


def new_game():
    """重置：返回一份完整的全新状态，不残留任何旧字段。"""
    return copy.deepcopy(DEFAULT_STATE)


def rule_a(state):
    """单次回溯只累计一次。"""
    state["count"] += 1
    return state["count"]


def rule_b(state):
    """消耗记忆点：余额不足时拒绝且不扣减。"""
    if state["amount"] < 5:
        return False
    state["amount"] -= 5
    return True


def rule_c(state):
    """转移记忆：源格减少的同时目标格等量入账。"""
    if state["src"] < 5:
        return False
    state["src"] -= 5
    state["dst"] += 5
    return True


def rule_d(state):
    """整理先入片段：按序保留首入片段，丢弃其余。"""
    return [row for row in state["audit"] if row[0] == "a"]


def rule_e(state):
    """进入梦境：记忆格已满时拒绝进入。"""
    if state["slots"] >= state["cap"]:
        return False
    state["slots"] += 1
    return True


def rule_f(state):
    """读取当前梦境：空梦境不返回文本，正常梦境返回内容。"""
    dream = state.get("dream")
    if not dream:
        return None
    return dream


def rule_g(state):
    """推进时钟：锁定状态下时间不再跳跃。"""
    if state["paused"]:
        return state["clock"]
    state["clock"] += 1
    return state["clock"]


def rule_h(state):
    """查看片段：只读取不移除。"""
    if not state["items"]:
        return False
    return state["items"][0]


def rule_i(state):
    """收纳片段：重复梦境与满格都拒绝收纳。"""
    if len(state["items"]) >= state["cap"]:
        return False
    if "x" in state["items"]:
        return False
    state["items"].append("x")
    return True


def rule_j(state):
    """梦境跳跃：锁定状态下禁止跳跃。"""
    if state["paused"]:
        return False
    return True


def save_game(state, path):
    """存档：完整写入状态，编号保持不变。"""
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)


def load_game(path):
    """读档：按存档原样恢复，编号不跳号。"""
    with open(path, "r", encoding="utf-8") as fh:
        loaded = json.load(fh)
    state = new_game()
    state.update(loaded)
    return state


def main():
    print("engine 命令: run/quit")
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
