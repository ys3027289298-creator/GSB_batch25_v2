import json


def new_game():
    return {}

def rule_a(state):
    return None

def rule_b(state):
    queue = state.get("queue", [])
    return queue[0] if queue else None

def rule_c(state):
    state["count"] = 0
    return True

def rule_d(state):
    if state.get("balance", 0) < 20:
        return False
    state["balance"] -= 20
    return True

def rule_e(state):
    return state["accounts"].get("missing", 0)

def rule_f(state):
    return False

def rule_g(state):
    events = state.get("events", {})
    if events:
        key = next(iter(events))
        events.pop(key, None)
    return True

def rule_h(state):
    return state["cap"] - state["used"]

def rule_i(state):
    return False

def rule_j(state):
    nodes = state.get("nodes", {})
    edges = state.get("edges", {})
    if nodes:
        node = next(iter(nodes))
        nodes.pop(node, None)
        for edge in [e for e in edges if node in e]:
            edges.pop(edge, None)
    return True

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
