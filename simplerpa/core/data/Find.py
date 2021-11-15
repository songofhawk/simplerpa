from __future__ import annotations

import time

# from core.action.ActionSystem import ActionSystem
from . import Misc
from .StateBlockBase import StateBlockBase
from simplerpa.core.action import ActionMouse
from simplerpa.core.data.Action import Execution, Action
from simplerpa.core.detection.ImageDetection import ImageDetection
from simplerpa.core.detection.OcrDetection import OcrDetection
from simplerpa.core.detection.ColorDetection import ColorDetection
from simplerpa.core.detection.WindowDetection import WindowDetection
from simplerpa.core.share import list_util
from ..action.ActionSystem import ActionSystem


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
    image: ImageDetection
    ocr: OcrDetection
    color: ColorDetection
    window: WindowDetection
    scroll: Scroll
    fail_action: Execution
    result_name: str = None
    find_mode: str = "All"
    foreach: Misc.ForEach = None

    def do(self, do_fail_action):
        results = []
        found_any = False
        found_all = True
        if self.image is not None:
            res = self._do_once(self.image, do_fail_action)
            found_any = found_any or (res is not None)
            found_all = found_all and (res is not None)
            list_util.append_to(results, res)

        if self.ocr is not None:
            res = self._do_once(self.ocr, do_fail_action)
            found_any = found_any or (res is not None)
            found_all = found_all and (res is not None)
            list_util.append_to(results, res)

        if self.color is not None:
            res = self._do_once(self.color, do_fail_action)
            found_any = found_any or (res is not None)
            found_all = found_all and (res is not None)
            list_util.append_to(results, res)

        if self.window is not None:
            res = self._do_once(self.window, do_fail_action)
            found_any = found_any or (res is not None)
            found_all = found_all and (res is not None)
            list_util.append_to(results, res)

        if len(results) == 0:
            return None
        else:
            final_result = results if len(results) > 1 else results[0]
            if self.find_mode == "All" and found_all:
                if self.result_name is not None:
                    Action.save_call_env({self.result_name: final_result})
                return final_result
            elif self.find_mode == "Any" and found_any:
                if self.result_name is not None:
                    Action.save_call_env({self.result_name: final_result})
                return final_result
            else:
                return None

    def _do_once(self, detection, do_fail_action):
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

        size = len(results)
        if size == 0:
            if do_fail_action:
                Action.call(self.fail_action)
            return None
        elif size == 1:
            return results[0]
        else:
            return results

    def flow_control_fail_action(self):
        # 找到当前find节点中的影响流程运行的fail_action并返回
        # 一个find节点（即使是list组成的节点）中，只能有一个影响流程运行的fail_action
        fail_action = self.fail_action
        if fail_action is None:
            return None

        if isinstance(fail_action, Action) and fail_action.is_flow_control:
            return fail_action
        if isinstance(fail_action, list):
            for one_action in fail_action:
                if one_action.is_flow_control:
                    return one_action
        return None
