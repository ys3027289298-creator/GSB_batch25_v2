import json


def new_game():
    return {}

def event_a(state):
    return max(state["accounts"], default=-1) + 1

def event_b(state):
    return not state.get("locked", True)

def event_c(state):
    state["events"].clear()
    return True

def event_d(state):
    return state["cap"] - state["used"]

def event_e(state):
    return not state.get("fired", True)

def event_f(state):
    state["nodes"].pop(1, None)
    state["edges"] = {
        edge: weight
        for edge, weight in state["edges"].items()
        if 1 not in edge
    }
    return True

def event_g(state):
    return state.get("target")

def event_h(state):
    return state["queue"][0]

def event_i(state):
    state["count"] = 0
    return True

def event_j(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

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
