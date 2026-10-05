import json


def new_game():
    return {}

def rule_a(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] = state.get("dst", 0) + 10
    return True

def rule_b(state):
    return not state.get("closed", False)

def rule_c(state):
    if state.get("forged"):
        return False
    state["forged"] = True
    return True

def rule_d(state):
    return bool(state.get("orders"))

def rule_e(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def rule_f(state):
    return bool(state.get("furnace"))

def rule_g(state):
    if state.get("charged"):
        return False
    state["charged"] = True
    return True

def rule_h(state):
    return state["queue"].pop(0)

def rule_i(state):
    return len(state["items"])

def rule_j(state):
    current = state["next_id"]
    state["next_id"] += 1
    return current

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
