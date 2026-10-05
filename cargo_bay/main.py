import json


def new_game():
    return {}

def cmd_a(state):
    return [row for row in state["audit"] if row[0] == "a"]

def cmd_b(state):
    return state["slots"] < state["cap"]

def cmd_c(state):
    return not state.get("items")

def cmd_d(state):
    if state.get("paused"):
        return state["clock"]
    state["clock"] += 1
    return state["clock"]

def cmd_e(state):
    items = state.get("items")
    if not items:
        return False
    items.pop(0)
    return True

def cmd_f(state):
    items = state["items"]
    if len(items) >= state["cap"]:
        return False
    if "x" in items:
        return False
    state["items"].append("x")
    return True

def cmd_g(state):
    return not state.get("paused", False)

def cmd_h(state):
    state["count"] += 1
    return state["count"]

def cmd_i(state):
    if state["amount"] < 5:
        return False
    state["amount"] -= 5
    return True

def cmd_j(state):
    if state["src"] < 5:
        return False
    state["src"] -= 5
    state["dst"] += 5
    return True

def reset_game(state):
    state.clear()
    state.update(new_game())
    return state

def save_game(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)
    return True

def load_game(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

def main():
    print("main 命令: run/quit")
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
