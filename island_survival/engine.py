import json


def new_game():
    return {}

def rule_a(state):
    items = state.get("items")
    if not items:
        return None
    return items

def rule_b(state):
    if state.get("acted"):
        return False
    state["acted"] = True
    return True

def rule_c(state):
    return state["queue"].pop(0)

def rule_d(state):
    return len(state["items"])

def rule_e(state):
    event_id = state["next_id"]
    state["next_id"] += 1
    return event_id

def rule_f(state):
    if state["src"] < 10:
        return False
    state["src"] -= 10
    state["dst"] += 10
    return True

def rule_g(state):
    return not state.get("closed", False)

def rule_h(state):
    if state.get("reset"):
        return False
    events = state.get("events")
    if events is not None:
        events.clear()
    state["reset"] = True
    return True

def rule_i(state):
    return state.get("used", 0) < state.get("cap", 0)

def rule_j(state):
    return min(state["events"], key=lambda key: state["events"][key][0])

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
