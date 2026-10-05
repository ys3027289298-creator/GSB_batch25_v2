import json


def new_game():
    return {}

def action_a(state):
    return state["queue"].pop(0)

def action_b(state):
    return len(state["items"])

def action_c(state):
    return state["next_id"]

def action_d(state):
    if state["src"] >= 10:
        state["src"] -= 10
        return True
    return False

def action_e(state):
    return not state["closed"]

def action_f(state):
    if state.get("_explored"):
        return False
    state["_explored"] = True
    return True

def action_g(state):
    return None

def action_h(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def action_i(state):
    if not state.get("items"):
        return False
    state["items"] = []
    return True

def action_j(state):
    if state.get("_done"):
        return False
    state["_done"] = True
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
