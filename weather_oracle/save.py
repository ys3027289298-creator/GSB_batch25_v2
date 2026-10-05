import json


def new_game():
    return {}

def state_a(state):
    if state["amount"] < 5:
        return False
    state["amount"] -= 5
    return True

def state_b(state):
    state["src"] -= 5
    state["dst"] += 5
    return True

def state_c(state):
    return [row for row in state["audit"] if row[0] == "a"]

def state_d(state):
    return state["slots"] < state["cap"]

def state_e(state):
    state.clear()
    return True

def state_f(state):
    if not state["paused"]:
        state["clock"] += 1
    return state["clock"]

def state_g(state):
    return state.get("forecast", False)

def state_h(state):
    if len(state["items"]) >= state["cap"]:
        return False
    state["items"].append("x")
    return True

def state_i(state):
    return not state.get("paused", False)

def state_j(state):
    state["count"] += 1
    return state["count"]

def main():
    print("save 命令: run/quit")
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
