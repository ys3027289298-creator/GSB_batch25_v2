"""钟楼报时状态机。

状态保存在纯 JSON 可序列化的 dict 中，键名固定：
    phase     运行阶段：stopped / running / paused
    used      发条已上弦的齿轮数
    cap       发条最大容量（齿轮总数）
    events    待敲钟事件 {编号: True}
    struck      已敲钟编号集合（防重复敲钟）
    queue     待播放钟声队列（先到先播）
    nodes     齿轮节点 {编号: True}
    edges     齿轮啮合边 {(甲, 乙): 齿数}
    count     单次报时累计次数
    balance   余额
    accounts  账户表 {户名: 账号}
"""

import json

PHASE_STOPPED = "stopped"
PHASE_RUNNING = "running"
PHASE_PAUSED = "paused"

TRANSITIONS = {
    PHASE_STOPPED: (PHASE_RUNNING,),
    PHASE_RUNNING: (PHASE_PAUSED, PHASE_STOPPED),
    PHASE_PAUSED: (PHASE_RUNNING, PHASE_STOPPED),
}

WIND_COST = 20

DEFAULTS = {
    "phase": PHASE_STOPPED,
    "used": 0,
    "cap": 0,
    "events": {},
    "struck": [],
    "queue": [],
    "nodes": {},
    "edges": {},
    "count": 0,
    "balance": 0,
    "accounts": {},
}


class IllegalTransition(Exception):
    """不允许的运行阶段切换。"""


def new_state():
    return {key: (value.copy() if isinstance(value, (dict, list)) else value)
            for key, value in DEFAULTS.items()}


class ClockTower:
    """钟楼状态机：所有规则都先校验阶段与守卫，再改状态。"""

    def __init__(self, state=None):
        self.state = new_state() if state is None else state
        self._normalize()

    def _normalize(self):
        for key, value in DEFAULTS.items():
            if key not in self.state:
                self.state[key] = value.copy() if isinstance(value, (dict, list)) else value

    # ---- 运行阶段 ----

    def transition(self, target):
        allowed = TRANSITIONS[self.state["phase"]]
        if target not in allowed:
            raise IllegalTransition(
                "%s -> %s 不允许" % (self.state["phase"], target))
        self.state["phase"] = target

    def start(self):
        self.transition(PHASE_RUNNING)

    def pause(self):
        self.transition(PHASE_PAUSED)

    def resume(self):
        self.transition(PHASE_RUNNING)

    def stop(self):
        self.transition(PHASE_STOPPED)

    # ---- 发条 ----

    def remaining(self):
        """剩余可上弦齿轮数：cap - used，不少算一。"""
        return self.state["cap"] - self.state["used"]

    def can_wind(self):
        return self.remaining() > 0

    def wind(self):
        if not self.can_wind():
            return False
        self.state["used"] += 1
        return True

    def pay_wind_cost(self):
        """余额不足则不扣费并返回 False。"""
        if self.state["balance"] < WIND_COST:
            return False
        self.state["balance"] -= WIND_COST
        return True

    # ---- 走时 ----

    def tick(self):
        """仅运行阶段走时；暂停或停止时不走。"""
        if self.state["phase"] != PHASE_RUNNING:
            return False
        if self.state["used"] > 0:
            self.state["used"] -= 1
        return True

    # ---- 敲钟与钟声 ----

    def can_strike(self, event):
        """事件存在且未敲过才允许敲，避免重复敲钟。"""
        return event in self.state["events"] and event not in self.state["struck"]

    def strike(self, event):
        if not self.can_strike(event):
            return False
        self.state["struck"].append(event)
        self.state["count"] += 1
        return True

    def play_next_chime(self):
        """播放最早到达的钟声并出队；空队列返回 None。"""
        if not self.state["events"]:
            return None
        first = min(self.state["events"])
        return self.state["events"].pop(first)

    def peek_next_chime(self):
        """查看队首钟声但不出队；空队列返回 None。"""
        if not self.state["queue"]:
            return None
        return self.state["queue"][0]

    # ---- 齿轮 ----

    def remove_gear(self, gear):
        """拆除齿轮节点，并清掉与之啮合的边。"""
        self.state["nodes"].pop(gear, None)
        for edge in [edge for edge in self.state["edges"] if gear in edge]:
            del self.state["edges"][edge]
        return True

    # ---- 钟面 ----

    def face_value(self):
        """空钟面返回 None，而不是文本。"""
        if not self.state["nodes"]:
            return None
        return min(self.state["nodes"])

    # ---- 计数与账户 ----

    def reset_count(self):
        self.state["count"] = 0
        return True

    def account_number(self, name):
        """账户不存在时返回 0，不跳号。"""
        return self.state["accounts"].get(name, 0)

    # ---- 存档 ----

    def save(self, path):
        data = dict(self.state)
        data["edges"] = {json.dumps(list(edge)): value
                         for edge, value in self.state["edges"].items()}
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, sort_keys=True)

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        if isinstance(data.get("edges"), dict):
            data["edges"] = {tuple(json.loads(key)): value
                             for key, value in data["edges"].items()}
        return cls(data)
