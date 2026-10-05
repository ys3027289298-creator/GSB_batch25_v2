import json


def new_game():
    return {}

def action_a(state):
    state["count"] = 0
    return True

def action_b(state):
    if state.get("balance", 0) < 20:
        return False
    state["balance"] -= 20
    return True

def action_c(state):
    return state["accounts"].get("missing", 0)

def action_d(state):
    if not state:
        return False
    return True

def action_e(state):
    state["events"].clear()
    return True

def action_f(state):
    return state["cap"] - state["used"]

def action_g(state):
    if not state:
        return False
    return True

def action_h(state):
    state["nodes"].pop(1, None)
    edges = state.get("edges", {})
    for edge in [e for e in edges if 1 in e]:
        del edges[edge]
    return True

def action_i(state):
    return None

def action_j(state):
    return state["queue"][0]

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
