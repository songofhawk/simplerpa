from simplerpa.core.data.Action import Action, Execution
from simplerpa.core.data.AutoBase import AutoBase


class DetectResult:
    """
    Attributes:
        detected (bool): 标识是否检测到了指定内容
    """
    # detected: bool = False


class Detection(AutoBase):
    """
    检测基础类，有ColorDetection, ImageDetection, OcrDetection, WindowDetection等子类，用于检测页面上的特定内容。
    Attributes:
        template (str): 模板
        find_all (bool): 是否查找所有结果,如果为False, 那么只返回第一个，缺省为False
        for_not_exist (bool): 检测结果取反，也就是检测不到的情况下，正常返回，检测到了触发fail_action，缺省为False；如果这个属性设置为True，那么find_all属性就失效了
        debug (bool): 执行检测do方法的时候，将相关信息记录到日志中（文本），或者单独保存文件（图片）
    """
    detect_all: bool = False
    for_not_exist: bool = False
    debug: bool = False
    fail_action: Execution = None

    def __init__(self):
        self.project = None
        self._template_full_path = None

    def do(self):
        result = self.do_detection()
        if self.for_not_exist:
            if result is not None and self.fail_action is not None:
                Action.call(self.fail_action)
        else:
            if result is None and self.fail_action is not None:
                Action.call(self.fail_action)

        return result

    def do_detection(self):
        raise NotImplementedError('"do_detection" method must be implemented by a sub class of Detection')
