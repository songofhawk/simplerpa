from __future__ import annotations
import time

from simplerpa.core.action import ActionMouse
from simplerpa.core.action.ActionClipboard import ActionClipboard
from simplerpa.core.action.ActionError import ActionError
from simplerpa.core.action.ActionExcel import ActionExcel
from simplerpa.core.action.ActionImage import ActionImage
from simplerpa.core.action.ActionKeyboard import ActionKeyboard
from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.action.ActionWindow import ActionWindow
from simplerpa.core.const import MOUSE
from simplerpa.core.data.ScreenRect import ScreenRect


class Action:
    """
    执行操作基础类，有Evaluation和Execution两个子类，分别对应有返回结果和没有返回结果的操作。在本基础类中，还定义了所有具体的操作方法名，这些方法可以在Action类型的配置节点中直接调用。具体的参数会在对应的类中介绍

    Attributes:
        move (ActionMouse.move): 移动鼠标，例如 move(354,267)
        raise_error (ActionError.trigger): 引发异常，例如raise_error('钉钉不是当前页面')
        click (ActionMouse.click): 点击鼠标，例如 click(354,267)，click执行的时候，鼠标指针也会被移动到指定位置
        dbclick (ActionMouse.dbclick): 双击鼠标，例如 dbclick(354,267)
        rightclick (ActionMouse.rightclick): 右键点击鼠标，例如 rightclick(354,267)
        hotkey (ActionKeyboard.hotkey): 点击键盘热键，例如 hotkey("alt","tab")
        type (ActionKeyboard.type): 输入字符串（模拟键盘输入，参数是整个字符串），例如 type("张三")
        press (ActionKeyboard.press): 点击键盘（指定一个键），例如 press("a"), press("ctrl", 2)
        ocr (ActionImage.ocr): 识别给定图片中的文字，例如 x = ocr(week_report.clip)，这里week_report.clip是上一步截图得到的图像数据，x是识别出来的文字
        print (print): 打印信息到控制台，就是python内置的print方法
        find_template (ActionImage.find_one_template): 在指定图像中，查找另外一幅图像，例如 find_template(snapshot_image, week_report.clip).rect，这里要从图像snapshot_image中找到图像week_report.clip， 返回结果里有有个rect属性，标识了找到的片段在屏幕上的位置
        snapshot (ActionScreen.snapshot_cv): 屏幕截图，例如 snapshot(snapshot_rect)，传入一个表示屏幕矩形位置的ScreenRect对象，返回对应位置的图像
        log_image (ActionImage.log_image): 保存图片到文件，例如 log_image("snapshot", snapshot_image)，把图像保存到指定文件
        ScreenRect (ScreenRect): 新建一个ScreenRect对象，例如 snapshot_rect = ScreenRect(65, 298, 221, 761)，这个对象接受4个参数，分别是left, right, top, bottom
        wait (time.sleep): 等待指定时间（秒），例如 wait(0.5)，执行到这里会等待（休眠）指定的秒数
        copy (ActionClipboard.copy): 复制，例如 copy(x)，把指定的字符串复制到剪贴板
        paste (ActionClipboard.paste): 粘贴，例如 x = paste(), 把剪贴板里的内容变成字符串返回（注意并不是在界面当前位置粘贴，如果需要这个效果，可以调用 hotkey("ctrl","v") ）
        locate_state (ActionError.locate_state): 定位当前处于哪个State，例如 locate_state('没有找到钉钉窗口')，此时程序会中止正常的状态迁移，而是遍历当前状态层级，查找有可能处于哪个状态，并跳转到那个状态继续执行；参数字符串会输出到控制台，
        set_window_pos (ActionWindow.set_window_pos): 设置窗口的位置和大小，例如 set_window_pos(find_result.hwnd, 0, 0, 1024, 768)，这里的hwnd通常是WindowDetection返回的窗口句柄，通过这个函数，指定窗口的top,left,width,height坐标

    """
    func_dict = {
        'move': ActionMouse.move,
        'raise_error': ActionError.trigger,
        'click': ActionMouse.click,
        'dbclick': ActionMouse.dbclick,
        'rightclick': ActionMouse.rightclick,
        'hotkey': ActionKeyboard.hotkey,
        'type': ActionKeyboard.type,
        'press': ActionKeyboard.press,
        'ocr': ActionImage.ocr,
        'print': print,
        'find_template': ActionImage.find_one_template,
        'snapshot': ActionScreen.snapshot_cv,
        'log_image': ActionImage.log_image,
        'ScreenRect': ScreenRect,
        'wait': time.sleep,
        'copy': ActionClipboard.copy,
        'paste': ActionClipboard.paste,
        'locate_state': ActionError.locate_state,
        'set_window_pos': ActionWindow.set_window_pos,
        'get_window_rect': ActionWindow.get_window_rect,
        'create_dataframe': ActionExcel.create_dataframe,
    }

    _call_env = {**func_dict, **{}}

    def __init__(self, action_str):
        self._action_str = action_str
        if action_str.startswith('locate_state'):
            self.is_flow_control = True
            self.is_locate_state = True
        else:
            self.is_flow_control = False
            self.is_locate_state = False

    def call_once(self, call_env=None):
        if call_env is not None:
            if isinstance(call_env, dict):
                self.save_call_env(call_env)
            else:
                raise RuntimeError(
                    'The argument in "call" method of "Action" object, should be a dict, but {} is passed'.format(
                        type(call_env)))
        return self.evaluate_exp()

    def evaluate_exp(self):
        raise RuntimeError('_evaluate_exp is an abstract method, can not be called in an Action object!')

    def _prepare_exp(self):
        self._call_env[MOUSE] = ActionMouse.position()

    @classmethod
    def save_call_env(cls, call_env):
        cls._call_env.update(call_env)

    @classmethod
    def get_call_env(cls, name):
        return cls._call_env[name]

    @classmethod
    def call(cls, actions: Action, call_env=None):
        if actions is None:
            return None
        if isinstance(actions, list):
            results = []
            for action in actions:
                result = action.call_once(call_env)
                results.append(result)
            return results
        elif isinstance(actions, Action):
            return actions.call_once(call_env)


class Evaluation(Action):
    """
    Action操作类的子类，执行以后会有返回值
    """

    def __init__(self, action_str):
        super().__init__(action_str)
        self.exp = compile(action_str, '', 'eval')

    def evaluate_exp(self):
        super()._prepare_exp()
        return eval(self.exp, {"__builtins__": {}}, Action._call_env)


class Execution(Action):
    """
    Action操作类的子类，执行以后没有返回值
    """

    def __init__(self, action_str):
        super().__init__(action_str)
        self.exp = compile(action_str, '', 'exec')

    def evaluate_exp(self):
        super()._prepare_exp()
        return exec(self.exp, {"__builtins__": {}}, Action._call_env)
