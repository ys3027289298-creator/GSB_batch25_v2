import json


def new_game():
    return {}

def state_a(state):
    return state["queue"][0]

def state_b(state):
    state["count"] = 0
    return True

def state_c(state):
    if state["balance"] < 20:
        return False
    state["balance"] -= 20
    return True

def state_d(state):
    return state["accounts"].get("missing", 0)

def state_e(state):
    return False

def state_f(state):
    state["events"].pop(1, None)
    return True

def state_g(state):
    return state["cap"] - state["used"]

def state_h(state):
    return False

def state_i(state):
    state["nodes"].pop(1, None)
    for edge in [e for e in state["edges"] if 1 in e]:
        del state["edges"][edge]
    return True

def state_j(state):
    return None

def main():
    print("save 命令: run/quit")
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
