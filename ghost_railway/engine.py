import json


def new_game():
    return {}

def rule_a(state):
    return None

def rule_b(state):
    return state["queue"][0]

def rule_c(state):
    state["count"] = 0
    return True

def rule_d(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def rule_e(state):
    return state["accounts"].get("missing", 0)

def rule_f(state):
    if state.get("paused", True):
        return False
    return True

def rule_g(state):
    if state["events"]:
        state["events"].pop(next(iter(state["events"])), None)
    return True

def rule_h(state):
    return state["cap"] - state["used"]

def rule_i(state):
    return state.get("eligible", False)

def rule_j(state):
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        del state["edges"][edge]
    return True

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
