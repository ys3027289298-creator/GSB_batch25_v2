import json


def new_game():
    return {}

def rule_a(state):
    return False

def rule_b(state):
    state["events"].pop(1, None)
    return True

def rule_c(state):
    return state["cap"] - state["used"]

def rule_d(state):
    return False

def rule_e(state):
    state["nodes"].pop(1, None)
    for edge in [e for e in state["edges"] if 1 in e]:
        state["edges"].pop(edge, None)
    return True

def rule_f(state):
    return None

def rule_g(state):
    return state["queue"][0] if state["queue"] else None

def rule_h(state):
    state["count"] = 0
    return True

def rule_i(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def rule_j(state):
    return state["accounts"].get("missing", 0)

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
