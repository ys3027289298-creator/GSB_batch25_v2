import json


def new_game():
    return {}

def action_a(state):
    return state["cap"] - state["used"]

def action_b(state):
    intel = state.get("intel", [])
    return len(intel) != len(set(intel))

def action_c(state):
    state["nodes"].pop(1, None)
    state["edges"] = {k: v for k, v in state["edges"].items() if 1 not in k}
    return True

def action_d(state):
    intel = state.get("intel")
    if not intel:
        return None
    return intel

def action_e(state):
    return state["queue"][0]

def action_f(state):
    state["count"] = 0
    return True

def action_g(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def action_h(state):
    return state["accounts"].get("missing", 0)

def action_i(state):
    return state.get("locked", False)

def action_j(state):
    state["events"].pop(1, None)
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
