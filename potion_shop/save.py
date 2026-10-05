import json


def new_game():
    return {}

def state_a(state):
    return not state.get("closed", False)

def state_b(state):
    events = state.setdefault("events", {})
    if events:
        return False
    events[1] = True
    return True

def state_c(state):
    order = state.get("order")
    if not order:
        return False
    return order

def state_d(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def state_e(state):
    return bool(state.get("records"))

def state_f(state):
    if state.get("served"):
        return False
    state["served"] = True
    return True

def state_g(state):
    return state["queue"].pop(0)

def state_h(state):
    return len(state["items"])

def state_i(state):
    return state["next_id"]

def state_j(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

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
