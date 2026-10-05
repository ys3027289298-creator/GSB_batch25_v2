import json


def new_game():
    return {}

def event_a(state):
    state["nodes"].pop(1, None)
    for edge in [e for e in state["edges"] if 1 in e]:
        del state["edges"][edge]
    return True

def event_b(state):
    return None

def event_c(state):
    return state["queue"][0]

def event_d(state):
    state["count"] = 0
    return True

def event_e(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def event_f(state):
    return state["accounts"].get("missing", 0)

def event_g(state):
    return False

def event_h(state):
    if state["events"]:
        del state["events"][next(iter(state["events"]))]
    return True

def event_i(state):
    return state["cap"] - state["used"]

def event_j(state):
    return False

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
