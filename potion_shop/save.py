import json


def new_game():
    return {}

def state_a(state):
    return not state["closed"]

def state_b(state):
    events = state["events"]
    if "b" in events:
        return False
    events["b"] = True
    return True

def state_c(state):
    return bool(state.get("orders"))

def state_d(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def state_e(state):
    return bool(state.get("recipes"))

def state_f(state):
    recipes = state.setdefault("recipes", [])
    if "f" in recipes:
        return False
    recipes.append("f")
    return True

def state_g(state):
    return state["queue"].pop(0)

def state_h(state):
    return len(state["items"])

def state_i(state):
    current = state["next_id"]
    state["next_id"] += 1
    return current

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
