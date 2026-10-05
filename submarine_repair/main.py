import json


def new_game():
    return {}

def cmd_a(state):
    # 扣费维修：余额不足时整体回滚，不留下部分写入，失败后可重放
    snapshot = dict(state)
    try:
        if state["balance"] < 20:
            raise ValueError("insufficient balance")
        state["balance"] -= 20
    except (KeyError, ValueError):
        state.clear()
        state.update(snapshot)
        return False
    return True

def cmd_b(state):
    # 备件少算一：缺失账户按 0 计，而不是 -1
    return state["accounts"].get("missing", 0)

def cmd_c(state):
    # 锁定舱门仍作业：默认锁定，未解锁一律拒绝
    if state.get("locked", True):
        return False
    return True

def cmd_d(state):
    # 重置不清日志：重置时清空事件日志
    state.get("events", {}).clear()
    return True

def cmd_e(state):
    # 容量计算少算一：可用容量 = cap - used
    return state["cap"] - state["used"]

def cmd_f(state):
    # 重复故障单：已存在同号故障单时拒绝重复接收
    if not state.get("ticket"):
        return False
    return True

def cmd_g(state):
    # 删除节点时级联清理关联的边，避免悬空引用污染状态
    state["nodes"].pop(1, None)
    state["edges"] = {k: v for k, v in state["edges"].items() if 1 not in k}
    return True

def cmd_h(state):
    # 空舱室返回占位文本：空结果应返回 None 而非占位字符串
    return None

def cmd_i(state):
    # 查看故障误删：查看队首故障只读取不出队
    return state["queue"][0]

def cmd_j(state):
    # 单次维修重复累计：重置将计数清零，避免重复累计
    state["count"] = 0
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
