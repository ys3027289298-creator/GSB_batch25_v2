import json


def new_game():
    return {}

def event_a(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def event_b(state):
    return len(state.get("queue", [])) < state.get("slots", 0)

def event_c(state):
    if state.get("executed"):
        return False
    state["executed"] = True
    return True

def event_d(state):
    return state["queue"].pop(0)

def event_e(state):
    return len(state["items"])

def event_f(state):
    return state["next_id"]

def event_g(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    return True

def event_h(state):
    return not state.get("closed", False)

def event_i(state):
    if state.get("viewed"):
        return False
    state["viewed"] = True
    return True

def event_j(state):
    return bool(state.get("command"))

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
