import json


def new_game():
    return {
        "events": {},
        "queue": [],
        "items": [],
        "slots": [],
        "command": "",
        "next_id": 1,
        "src": 0,
        "dst": 0,
        "closed": False,
        "action_counted": False,
    }

def event_a(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def event_b(state):
    command = state.get("command")
    if not command:
        return False
    queue = state.setdefault("queue", [])
    if command in queue:
        return False
    queue.append(command)
    return True

def event_c(state):
    slots = state.setdefault("slots", [])
    if len(slots) >= 1:
        return False
    slots.append(state.get("command", ""))
    return True

def event_d(state):
    return state["queue"][0]

def event_e(state):
    return len(state["items"])

def event_f(state):
    current = state["next_id"]
    state["next_id"] += 1
    return current

def event_g(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

def event_h(state):
    return not state.get("closed", False)

def event_i(state):
    if state.get("action_counted"):
        return False
    state["action_counted"] = True
    return True

def event_j(state):
    command = state.get("command", "")
    if not command:
        return False
    return command

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
