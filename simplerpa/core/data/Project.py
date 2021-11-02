from typing import List, Dict

from .Misc import State
from .ScreenRect import ScreenRect


class Project:
    """
    配置根节点，对应自动化项目的基本信息

    Attributes:
        name (str): 项目名称
        ver (int): 数字版本号
        screen_width (int): 屏幕宽度（如果设置了这个属性，项目运行时会首先调整分辨率）
        screen_height (int): 屏幕高度（如果设置了这个属性，项目运行时会首先调整分辨率）
        states (List[State]): 状态列表，项目启动后，将从第一个状态开始执行
    """
    name: str = None
    ver: int = 0
    screen_width: int
    screen_height: int
    range: ScreenRect = None
    time_scale: float = 1.0
    states: List[State] = []

    def __init__(self):
        self.all_states: Dict[int, State] = {}
        self.path_root = None
        self.executor = None

    # @property
    # def executor(self):
    #     return StateBlockBase.executor
    #
    # @executor.setter
    # def executor(self, executor):
    #     StateBlockBase.executor = executor

