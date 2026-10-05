"""宫廷阴谋事件流核心逻辑。"""

TRANSFER_AMOUNT = 10


def has_duplicate_plot(state):
    plots = state.get("plots", [])
    return len(plots) != len(set(plots))


def next_event_id(state):
    return min(state["events"].items(), key=lambda item: item[1][0])[0]


def has_pending_event(state):
    return bool(state.get("events"))


def count_event_once(state):
    if state.get("counted"):
        return False
    state["counted"] = True
    return True


def pop_oldest_plot(state):
    return state["queue"].pop(0)


def plot_count(state):
    return len(state["items"])


def allocate_event_id(state):
    next_id = state["next_id"]
    state["next_id"] += 1
    return next_id


def spend_influence(state):
    if state["src"] < TRANSFER_AMOUNT:
        return False
    state["src"] -= TRANSFER_AMOUNT
    state["dst"] = state.get("dst", 0) + TRANSFER_AMOUNT
    return True


def trigger_if_open(state):
    return not state.get("closed", False)


def reset_events(state):
    if state.get("cleared"):
        return False
    state["events"].clear()
    state["cleared"] = True
    return True
