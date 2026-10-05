import json


def new_game():
    return {}

def event_a(state):
    next_id = state["next_id"]
    state["next_id"] += 1
    return next_id

def event_b(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

def event_c(state):
    return not state["closed"]

def event_d(state):
    if state["events"].get("opened"):
        return False
    state["events"]["opened"] = True
    return True

def event_e(state):
    return list(state.get("treasures", []))

def event_f(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def event_g(state):
    return list(state.get("keys", []))

def event_h(state):
    if state.get("reset_done"):
        return False
    state["reset_done"] = True
    state["records"] = []
    return True

def event_i(state):
    return state["queue"].pop(0)

def event_j(state):
    return len(state["items"])

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
