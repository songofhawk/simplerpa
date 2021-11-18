from simplerpa.core.data.Action import Execution
from simplerpa.core.data.StateBlockBase import StateBlockBase


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
    # sub_states: List[State] = None
    max_time: int = None

    def __init__(self, to_str='next', action_str=None):
        self._trans_time = 0
        self.to = To(to_str)
        if action_str is not None:
            self.action = Execution(action_str)

    def count(self):
        self._trans_time += 1

    def reach_max_time(self):
        return False if self.max_time is None else self._trans_time >= self.max_time
