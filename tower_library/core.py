"""塔中图书馆检索核心逻辑。

所有可变状态都保存在 new_game() 返回的 dict 中（可 JSON 序列化），
save/load 在该持久化边界上做完整往返；模块不持有任何全局可变状态。
"""

import json

SHELF_CAPACITY = 3
START_CANDLES = 10
RETRIEVE_COST = 1


def new_game():
    return {
        "tomes": {},          # tome_id -> {"title": str, "shelf": str|None}
        "shelves": {},        # shelf -> [tome_id, ...]
        "arrival_queue": [],  # 待归档队列，先到先归档
        "archive": [],        # 已归档的 tome_id，按归档顺序
        "candles": START_CANDLES,
        "retrievals": 0,
        "paused": False,
        "next_id": 1,
        "capacity": SHELF_CAPACITY,
    }


def receive_tome(state, title):
    for tome in state["tomes"].values():
        if tome["title"] == title:
            return None
    tome_id = "tome-%d" % state["next_id"]
    state["next_id"] += 1
    state["tomes"][tome_id] = {"title": title, "shelf": None}
    state["arrival_queue"].append(tome_id)
    return tome_id


def archive_next(state, shelf):
    if not state["arrival_queue"]:
        return None
    shelf_list = state["shelves"].setdefault(shelf, [])
    if len(shelf_list) >= state["capacity"]:
        return None
    tome_id = state["arrival_queue"].pop(0)
    shelf_list.append(tome_id)
    state["tomes"][tome_id]["shelf"] = shelf
    state["archive"].append(tome_id)
    return tome_id


def view_shelf(state, shelf):
    ids = state["shelves"].get(shelf)
    if not ids:
        return None
    return [state["tomes"][tome_id]["title"] for tome_id in ids]


def view_tome(state, tome_id):
    tome = state["tomes"].get(tome_id)
    if tome is None:
        return None
    return dict(tome)


def retrieve(state, shelf):
    if state["paused"]:
        return None
    shelf_list = state["shelves"].get(shelf)
    if not shelf_list:
        return None
    if state["candles"] < RETRIEVE_COST:
        return None
    state["candles"] -= RETRIEVE_COST
    state["retrievals"] += 1
    tome_id = shelf_list.pop(0)
    return state["tomes"].pop(tome_id)


def pause(state):
    state["paused"] = True
    return True


def resume(state):
    state["paused"] = False
    return True


def reset(state):
    state.clear()
    state.update(new_game())
    return state


def save(state):
    return json.dumps(state, ensure_ascii=False, sort_keys=True)


def load(payload):
    state = new_game()
    state.update(json.loads(payload))
    return state


def main():
    print("core 命令: run/quit")
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
