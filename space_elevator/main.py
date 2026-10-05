import json


def new_game():
    return {}

def cmd_a(state):
    return len(state["items"])

def cmd_b(state):
    next_id = state["next_id"]
    state["next_id"] += 1
    return next_id

def cmd_c(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

def cmd_d(state):
    return not state["closed"]

def cmd_e(state):
    if state.get("requested"):
        return False
    state["requested"] = True
    return True

def cmd_f(state):
    return bool(state.get("car"))

def cmd_g(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def cmd_h(state):
    records = state.get("records")
    if not records:
        return False
    records.clear()
    return True

def cmd_i(state):
    if state.get("ran"):
        return False
    state["ran"] = True
    return True

def cmd_j(state):
    return state["queue"].pop(0)

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
