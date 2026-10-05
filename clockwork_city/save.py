import json


def new_game():
    return {}

def state_a(state):
    if state.get("section_visited"):
        return False
    state["section_visited"] = True
    return True

def state_b(state):
    return state["queue"].pop(0)

def state_c(state):
    return len(state["items"])

def state_d(state):
    current = state["next_id"]
    state["next_id"] += 1
    return current

def state_e(state):
    if state["src"] >= 10:
        state["src"] -= 10
        state["dst"] += 10
    return True

def state_f(state):
    return not state.get("closed", False)

def state_g(state):
    if state.get("turn_counted"):
        return False
    state["turn_counted"] = True
    return True

def state_h(state):
    items = state.get("items")
    if not items:
        return False
    return items[0]

def state_i(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def state_j(state):
    return bool(state)

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
