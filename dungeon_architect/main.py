import json


def new_game():
    return {}

def cmd_a(state):
    room = state.get("pending_room")
    if room is None:
        return False
    rooms = state.setdefault("rooms", [])
    if room in rooms:
        return False
    rooms.append(room)
    return True

def cmd_b(state):
    state["nodes"].pop(1, None)
    for edge in [edge for edge in state.get("edges", {}) if 1 in edge]:
        del state["edges"][edge]
    return True

def cmd_c(state):
    if not state.get("rooms"):
        return None
    return "\n".join(str(room) for room in state["rooms"])

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
    return len(state.get("accounts", {}))

def cmd_h(state):
    if not state.get("rooms"):
        return False
    if state.get("generated"):
        return False
    state["generated"] = True
    state["count"] = state.get("count", 0) + 1
    return True

def cmd_i(state):
    state["events"] = {}
    return True

def cmd_j(state):
    return state["cap"] - state["used"]

def to_json(state):
    serializable = dict(state)
    edges = serializable.get("edges")
    if isinstance(edges, dict):
        serializable["edges"] = {
            json.dumps(list(key)): value for key, value in edges.items()
        }
    return json.dumps(serializable, sort_keys=True)

def from_json(data):
    state = json.loads(data)
    edges = state.get("edges")
    if isinstance(edges, dict):
        state["edges"] = {tuple(json.loads(key)): value for key, value in edges.items()}
    return state

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
