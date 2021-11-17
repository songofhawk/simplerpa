from __future__ import annotations

from typing import List

from .StateBlockBase import StateBlockBase
from simplerpa.core.data.Action import Action, Execution, Evaluation
from simplerpa.core.data.Find import Find
from ..extractor import FormExtractor
from ..monitor.ImageMonitor import ImageMonitor
from ..monitor.Monitor import Monitor


class To(StateBlockBase):
    def __init__(self, _to='next'):
        self.is_next = False
        self.id = None
        self._to = _to
        self.parse()

    def parse(self):
        _to = self._to
        if _to == 'next':
            self.is_next = True
            return
        else:
            self.is_next = False

        if _to == 'end':
            self.id = None

        if isinstance(_to, int):
            self.id = _to
        elif _to.isdigit():
            self.id = int(self._to)


class Transition(StateBlockBase):
    """
    状态迁移配置节点，指定什么动作会触发迁移
    """
    action: Execution = None
    wait_before: int = None
    wait: int = None
    to: To
    sub_states: List[State] = None
    max_time: int = None

    def __init__(self, to_str='next'):
        self._trans_time = 0
        self.to = To(to_str)

    def count(self):
        self._trans_time += 1

    def reach_max_time(self):
        return False if self.max_time is None else self._trans_time >= self.max_time


class State(StateBlockBase):
    """
    状态节点，用于配置界面流中一个特定的页面

    Attributes:
        name (str): 状态（页面）名称
        id (int): 状态唯一标识
        check (Find): 检查是否真属于当前页面
        find (Find): 在当前页面中查找特定元素或者片段
        action (Action): 进入当前页面状态后，会采取什么操作（比如鼠标点击），但不会引起状态迁移，这里可以是一个操作，也可以是多个；如果需要多个操作，就配置为列表，操作会按列表顺序执行
        transition (Transition): 状态迁移配置
        foreach (ForEach): 在当前状态下，针对特定数据做循环
    """
    name: str = None
    id: int = -1
    check: Find
    monitor: ImageMonitor
    find: Find
    action: Execution
    transition: Transition
    foreach: ForEach
    form: FormExtractor.FormExtractor = None

    def __init__(self):
        # 缺省的Transition是to end
        self.transition = Transition()


class ForEach(StateBlockBase):
    in_items: Evaluation
    item: str
    action: Execution
    sub_states: List[State]

    def __init__(self):
        self.call_env = {}

    def do(self):
        items = self.in_items.call_once()
        item_name = 'item' if self.item is None else self.item
        if isinstance(items, list):
            for item in items:
                self.call_env[item_name] = item
                self._do_one()
        elif items is not None:
            self.call_env[item_name] = items
            self._do_one()
        else:
            return

    def _do_one(self):
        Action.call(self.action, self.call_env)

        sub_states = self.sub_states
        if sub_states is not None and len(sub_states) > 0:
            self.project.executor.drill_into_substates(sub_states)
