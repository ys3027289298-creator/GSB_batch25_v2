import json

import core


def new_game():
    return {}

def cmd_a(state):
    return core.has_duplicate_plot(state)

def cmd_b(state):
    return core.next_event_id(state)

def cmd_c(state):
    return core.has_pending_event(state)

def cmd_d(state):
    return core.count_event_once(state)

def cmd_e(state):
    return core.pop_oldest_plot(state)

def cmd_f(state):
    return core.plot_count(state)

def cmd_g(state):
    return core.allocate_event_id(state)

def cmd_h(state):
    return core.spend_influence(state)

def cmd_i(state):
    return core.trigger_if_open(state)

def cmd_j(state):
    return core.reset_events(state)

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
