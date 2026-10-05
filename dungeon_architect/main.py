import json


def new_game():
    return {}

def cmd_a(state):
    room = state.get("pending_room")
    rooms = state.setdefault("rooms", [])
    if room is None or room in rooms:
        return False
    rooms.append(room)
    return True

def cmd_b(state):
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state["edges"] if 1 in edge]:
        del state["edges"][edge]
    return True

def cmd_c(state):
    if not state.get("map"):
        return None
    return state["map"]

def cmd_d(state):
    return state["queue"][0]

def cmd_e(state):
    state["count"] = 0
    return True

def cmd_f(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def cmd_g(state):
    return state["accounts"].get("missing", 0)

def cmd_h(state):
    if state.get("paused", True):
        return False
    state["generated"] = state.get("generated", 0) + 1
    return True

def cmd_i(state):
    state["events"].clear()
    return True

def cmd_j(state):
    return state["cap"] - state["used"]

def save_game(state):
    return json.dumps(state, sort_keys=True)

def load_game(payload):
    return json.loads(payload)

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
