import json


def new_game():
    return {}

def action_a(state):
    return state["queue"].pop(0)

def action_b(state):
    return len(state["items"])

def action_c(state):
    current = state["next_id"]
    state["next_id"] += 1
    return current

def action_d(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

def action_e(state):
    return not state["closed"]

def action_f(state):
    if state.get("explored"):
        return False
    state["explored"] = True
    return True

def action_g(state):
    if not state.get("items"):
        return False
    return True

def action_h(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def action_i(state):
    items = state.get("items") or []
    if not items:
        return False
    return items[-1]

def action_j(state):
    if state.get("reset"):
        return False
    state["items"] = []
    state["reset"] = True
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
