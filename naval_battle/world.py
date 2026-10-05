import json


FLEET_CAP = 2


def new_game():
    return {
        "ships": set(),
        "fleet": [],
        "fleet_cap": FLEET_CAP,
        "sea": {},
        "round_settled": False,
        "queue": [],
        "ammo": 0,
        "next_id": 0,
        "src": 0,
        "dst": 0,
        "paused": False,
        "closed": False,
        "events": {},
        "items": [],
    }


def action_a(state, ship_id=None):
    if ship_id is None:
        registry = state["events"]
        ship_id = "ship"
    else:
        registry = state.setdefault("ships", set())
    if ship_id in registry:
        return False
    if isinstance(registry, set):
        registry.add(ship_id)
    else:
        registry[ship_id] = True
    return True


def action_b(state, ship_id=None):
    if ship_id is None:
        ship_id = state.get("staging")
        if ship_id is None:
            return False
    fleet = state.setdefault("fleet", [])
    cap = state.get("fleet_cap", FLEET_CAP)
    if len(fleet) >= cap or ship_id in fleet:
        return False
    fleet.append(ship_id)
    return True


def action_c(state):
    events = state["events"]
    return min(events.items(), key=lambda item: item[1][0])[0]


def action_d(state, coord=None):
    sea = state.setdefault("sea", {})
    if coord is None or not sea.get(coord):
        return False
    return sea[coord]


def action_e(state):
    if state.get("round_settled"):
        return False
    state["round_settled"] = True
    return True


def action_f(state):
    queue = state["queue"]
    if not queue:
        return None
    return queue[0]


def action_g(state):
    return len(state.get("items", []))


def action_h(state):
    return state["next_id"]


def action_i(state, amount=10):
    src = state.get("src", 0)
    dst = state.get("dst", 0)
    if src < amount:
        return False
    state["src"] = src - amount
    state["dst"] = dst + amount
    return True


def action_j(state):
    return not (state.get("paused") or state.get("closed"))


def main():
    print("world 命令: run/quit")
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
