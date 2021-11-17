from __future__ import annotations

from typing import List

from simplerpa.core.action import ActionMouse
from simplerpa.core.data.Action import Execution, Action
from simplerpa.core.detection.ColorDetection import ColorDetection
from simplerpa.core.detection.ImageDetection import ImageDetection
from simplerpa.core.detection.OcrDetection import OcrDetection
from simplerpa.core.detection.WindowDetection import WindowDetection
from simplerpa.core.share import list_util

from . import Misc
from .StateBlockBase import StateBlockBase
from ..action.ActionSystem import ActionSystem
from ..const import FIND_RESULT
from ..detection.Detection import Detection


class Scroll(StateBlockBase):
    """
    在查找（Find）过程中的滚动配置
    Attributes:
        one_page (int): 每页滚动的距离，单位是虚拟像素（根据屏幕分辨率可能有缩放）
        page_count (int): 滚动页数
        find_mode (str): 是否要在滚动的过程中，找出所有结果，缺省为"Any"；
        如果为"All"，表示要完成所有滚动，并且在每一页执行detection，保存检测结果；
        如果为"Any"，则只要有一页检测通过，就不再滚动了
    """
    one_page: int  #
    page_count: int  #
    find_mode: str = "Any"


class Repeat(StateBlockBase):
    """
    重复性地执行detections
    Attributes:
        interval (float): 重复间隔时间，单位为秒
        times (int): 重复执行次数，如果等于None则一直重复下去，直到detections找到结果为止
    """
    interval: float = 1
    times: int = None


class Find(StateBlockBase):
    """
    用于查找的基础配置，可以有不同的查找模式，在State节点中，它如果是check属性，则不保存查找结果，如果是find属性，则把查找结果，临时存入find_result

    Attributes:
        image (ImageDetection) : 图像检测，在当前页面中找指定图像片段，不一定要完全一致，可以指定相似度
        ocr (OcrDetection) : 文本检测，在当前页面的指定位置做OCR识别，然后查看是否有指定的文本
        color (ColorDetection) : 颜色检测，在当前页面的指定像素位置，查看是否符合定义的颜色
        window (WindowDetection) : 窗口检测，在当前页面查找指定title或者name的窗口

        scroll (Scroll) : 查找的时候，如果没找到，就滚动当前窗口，继续查找
        fail_action (Execution) : 如果什么没有找到，需要执行的操作
        result_name (str): 给检测结果一个变量名
    """
    detections: List[Detection] = None
    image: ImageDetection
    ocr: OcrDetection
    color: ColorDetection
    window: WindowDetection

    mode: str = "any"
    order: str = "asc"  # to support 'desc' and 'rand'
    result_name: str = None
    foreach: Misc.ForEach = None
    fail: Misc.Transition = None
    scroll: Scroll

    repeat: Repeat = None

    def __init__(self):
        self._prepared = False
        self.detections = []

    def _prepare(self):
        if self._prepared:
            return
        if self.image is not None:
            self.detections.append(self.image)
        if self.ocr is not None:
            self.detections.append(self.ocr)
        if self.color is not None:
            self.detections.append(self.color)
        if self.window is not None:
            self.detections.append(self.window)
        self._prepared = True

    def do(self):
        self._prepare()
        results = []

        times = 0
        max_times = 1 if self.repeat is None else self.repeat.times
        while times < max_times:
            for detect_one in self.detections:
                res_list = self._detect_once(detect_one)
                list_util.append_to(results, res_list)
                if len(res_list) > 0 and self.mode == "any":
                    break
            if len(results) > 0:
                final_result = results if len(results) > 1 else results[0]
                Action.save_call_env({FIND_RESULT: final_result})
                if self.result_name is not None:
                    Action.save_call_env({self.result_name: final_result})
                break
            else:
                Action.save_call_env({FIND_RESULT: None})

            times += 1
        return results

    def _detect_once(self, detection):
        if detection is None:
            return None
        results = []
        if self.scroll is None:
            detect_res = detection.do()
            list_util.append_to(results, detect_res)
        else:
            scroll = self.scroll
            # 有滚动的话，就按滚动页数执行循环
            count = scroll.page_count
            page = 0
            while True:
                # 如果滚动的时候，找到即返回，那么就检查detect_res是否为None
                # 如果滚动到指定页数，返回所有找到的结果，那么就不用检查detect_res了
                detect_res = detection.do()
                list_util.append_to(results, detect_res)
                if detect_res is not None and scroll.find_mode == "Any":
                    break
                page += 1
                if page < count:
                    # print('before scroll {}'.format(self.scroll.one_page))
                    ActionMouse.scroll(self.scroll.one_page)
                    ActionSystem.wait(1.5)
                    # print('-- after scroll')

        if self.foreach is not None:
            self.foreach.do()

        return results
