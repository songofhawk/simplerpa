from simplerpa.core.action.ActionWindow import ActionWindow
from simplerpa.core.data.ScreenRect import ScreenRect
from simplerpa.core.detection.Detection import Detection


class WindowResult:
    """
    WindowDetection的返回值对象

    Attributes:
        hwnd (int): 窗口句柄
    """
    hwnd: int

    def __init__(self, hwnd):
        self.hwnd = hwnd


class WindowDetection(Detection):
    """
    窗口检测，检测在当前环境中，是否有指定的窗口。
    如果current_only设置为True（缺省值），那么只检测当前窗口是否符合title或者win_class配置；
    如果current_only设置为False，那么就在整个桌面中寻找指定title或者win_class的窗口。
    如果结果找到了，就返回一个WindowResult对象，里面含有一个hwnd属性，保存了窗口句柄；
    如果结果没到到，则返回None

    Example:
        ```yaml
        # State的一个属性
        find:
          window:
            title: 钉钉
            debug: True
          fail_action: raise_error('没有找到钉钉窗口')
        ```
        或者
        ```yaml
        # State的一个属性
        check:
          - window:
              win_class: StandardFrame_DingTalk
              debug: True
            fail_action: locate_state('没有找到钉钉窗口')
        ```
    Attributes:
        current_only (bool): 是否只检测当前窗口，缺省为True；如果设置为False，则会在桌面所有打开的窗口中查找
        win_class (str): 窗口的win_class，可用spy++等工具查看
        title (str): 窗口标题，通常是显示在任务栏上的文字

    ```yaml
    result: 如果找到了，就返回一个WindowResult对象，如果没有找到，就返回None
    ```
    """

    current_only: True
    win_class: ScreenRect
    title: str

    def do(self, find_all=False):
        if self.current_only:
            check_pass = True
            hwnd = ActionWindow.get_current_window()
            msg = ''
            if self.title:
                title = ActionWindow.get_window_title(hwnd)
                if title != self.title:
                    check_pass = check_pass or False
                else:
                    check_pass = check_pass or True
                if self.debug:
                    msg += '实际title:"{}", 预期title:"{}"'.format(title, self.title)

            if self.win_class:
                win_class = ActionWindow.get_window_class(hwnd)
                if win_class != self.win_class:
                    check_pass = check_pass or False
                else:
                    check_pass = check_pass or True
                if self.debug:
                    msg += '' if msg=='' else ', '
                    msg += '实际class:"{}", 预期class:"{}"'.format(win_class, self.win_class)

            if check_pass:
                if self.debug:
                    print('检查当前窗口成功，{}'.format(msg))
                return WindowResult(hwnd)
            else:
                if self.debug:
                    print('检查当前窗口失败，{}'.format(msg))
                return None
        else:
            hwnd = ActionWindow.find_window(self.title, self.win_class)
            if hwnd is None:
                if self.debug:
                    print('检测窗口失败，预期title:"{}", 预期class:"{}'.format(self.title, self.win_class))
                return None
            else:
                if self.debug:
                    print('检测窗口成功，预期title:"{}", 预期class:"{}'.format(self.title, self.win_class))
                ActionWindow.set_current_window(hwnd)
                return WindowResult(hwnd)

