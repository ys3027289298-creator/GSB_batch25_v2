import json

import core


def new_game():
    return core.new_state()


def rule_a(state):
    return core.ClockTower(state).can_strike(1)


def rule_b(state):
    return core.ClockTower(state).play_next_chime()


def rule_c(state):
    return core.ClockTower(state).remaining()


def rule_d(state):
    return core.ClockTower(state).can_wind()


def rule_e(state):
    return core.ClockTower(state).remove_gear(1)


def rule_f(state):
    return core.ClockTower(state).face_value()


def rule_g(state):
    return core.ClockTower(state).peek_next_chime()


def rule_h(state):
    return core.ClockTower(state).reset_count()


def rule_i(state):
    return core.ClockTower(state).pay_wind_cost()


def rule_j(state):
    return core.ClockTower(state).account_number("missing")


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
