import json


def new_game():
    return {
        "accounts": {},
        "slots_used": 0,
        "slots_cap": 0,
        "used": 0,
        "cap": 0,
        "events": {},
        "nodes": {},
        "edges": {},
        "target": None,
        "locked": False,
        "queue": [],
        "count": 0,
        "score": 0,
        "balance": 0,
    }

def event_a(state):
    return state["accounts"].get("missing", 0)

def event_b(state):
    if state["slots_used"] >= state["slots_cap"]:
        return False
    state["slots_used"] += 1
    return True

def event_c(state):
    for key in list(state["events"]):
        del state["events"][key]
        return True
    return False

def event_d(state):
    return state["cap"] - state["used"]

def event_e(state):
    if not state["locked"]:
        return False
    state["locked"] = False
    return True

def event_f(state):
    removed = state["nodes"].pop(1, None)
    if removed is None:
        return False
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        del state["edges"][edge]
    return True

def event_g(state):
    return state["target"]

def event_h(state):
    if not state["queue"]:
        return None
    return state["queue"][0]

def event_i(state):
    state["count"] = 0
    return True

def event_j(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

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
