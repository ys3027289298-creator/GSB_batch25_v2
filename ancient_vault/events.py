import json


def new_game():
    return {
        "next_id": 0,
        "src": 0,
        "dst": 0,
        "closed": False,
        "opened": False,
        "treasure": None,
        "events": {},
        "records": [],
        "keys": [],
        "queue": [],
        "items": [],
    }

def event_a(state):
    return state["next_id"]

def event_b(state):
    if state["src"] >= 10:
        state["src"] -= 10
        state["dst"] += 10
        return True
    return False

def event_c(state):
    return not state["closed"]

def event_d(state):
    if state["opened"]:
        return False
    state["opened"] = True
    return True

def event_e(state):
    return state["treasure"]

def event_f(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def event_g(state):
    state["records"] = []
    return False

def event_h(state):
    if state["keys"]:
        return False
    state["keys"].append("key")
    return True

def event_i(state):
    return state["queue"].pop(0)

def event_j(state):
    return len(state["items"])

def save_state(state, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(state, fh)

def load_state(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)

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
