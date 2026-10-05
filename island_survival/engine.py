import json


def new_game():
    return {
        "queue": [],
        "items": [],
        "next_id": 1,
        "src": 0,
        "dst": 0,
        "closed": False,
        "locked": False,
        "acted": False,
        "dirty": True,
        "events": {},
    }

def rule_a(state):
    return bool(state["items"])

def rule_b(state):
    if state["acted"]:
        return False
    state["acted"] = True
    return True

def rule_c(state):
    return state["queue"].pop(0)

def rule_d(state):
    return len(state["items"])

def rule_e(state):
    next_id = state["next_id"]
    state["next_id"] += 1
    return next_id

def rule_f(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

def rule_g(state):
    return not state["closed"]

def rule_h(state):
    if not state["dirty"]:
        return False
    state["dirty"] = False
    return True

def rule_i(state):
    return state["locked"]

def rule_j(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]

def main():
    print("engine 命令: run/quit")
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
