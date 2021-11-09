from typing import Tuple

import PIL
import cv2
import numpy as np
from core.data.StateBlockBase import StateBlockBase
from simplerpa.core.action.ActionImage import ActionImage
from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.data import Action
from simplerpa.core.data.ScreenRect import ScreenRect, Vector
from simplerpa.core.detection.Detection import Detection, DetectResult


class ImageDetectResult(DetectResult):
    """
    Attributes:
        rect_on_image: 结果图像在指定区域内的相对位置
        rect_on_screen: 结果图像在屏幕上的位置
        image: 结果图像
        clip: 额外截取的图像片段
        clip_on_image: clip图像在指定区域内的相对位置
        clip_on_screen: clip图像在屏幕上的位置
        scale: 在什么缩放比例下，得到的当前检测结果
    """
    rect_on_image: ScreenRect = None
    rect_on_screen: ScreenRect = None
    image = None
    clip = None
    clip_on_image: ScreenRect = None
    clip_on_screen: ScreenRect = None
    scale: float = None
    priority: float = None


class ToBinary(StateBlockBase):
    background: Tuple[int, int, int] = None
    foreground: Tuple[int, int, int] = None
    tolerance: float = 0.01

    def __init__(self):
        pass

    def convert(self, image):
        # bk_bgr = np.array([self.background[2], self.background[1], self.background[0]])
        return ActionImage.to_binary(image, self.foreground, self.background, self.tolerance)


class ImageDetection(Detection):
    """
    图像检测，在当前页面的指定范围内，查找匹配的图像。如果找到了，会返回一个result结构，

    Example:
        ```yaml
        # State的一个属性
          image:
            snapshot: !rect l:65, r:298, t:221, b:761
            template: auto_dingding/work_report_text_snippet.png
            confidence: 0.8
            keep_clip: result.rect_on_image.snap_left(45)
        ```

    Attributes:
        snapshot (ScreenRect): 屏幕截图位置，限定查找范围，可以指定得大一些，程序会在指定范围内查找图像
        template (str): 要查找的图像模板文件（支持相对路径）
        rect (Vector): 和color是一组，表示要检测一个纯色块，Vector里的x表示宽，y表示高
        color (Tuple[int,int,int]): 和rect是一组，表示要检测一个纯色块，color按照(r,g,b)的顺序指定颜色
        confidence (float): 置信度，查找图像的时候，并不需要严格一致，程序会模糊匹配，并返回一个置信度（0 ~ 1之间的一个数值），置信度大于给定的数值，才会认为找到了
        keep_clip (Action.Evaluation): 根据返回结果，额外保持一个截图片段（比如已经查到图像左侧100个像素的区域）

    """
    template: str
    rect: Vector
    color: Tuple[int, int, int] = (0, 0, 0)
    snapshot: ScreenRect
    confidence: float = 0.8
    keep_clip: Action.Evaluation
    auto_scale: Tuple[float, float] = None
    scale: Action.Evaluation = 1
    priority: str = None
    grayscale: bool = False
    to_binary: ToBinary = None

    def do_detection(self, source_image=None):
        if source_image is None:
            snapshot_image = ActionScreen.snapshot(self.snapshot.evaluate())
            source_image = ActionImage.pil_to_cv(snapshot_image)

        if self.scale is not None:
            scale = self.scale.evaluate_exp() if isinstance(self.scale, Action.Evaluation) else self.scale
        else:
            scale = None

        if self.template is not None:
            res = self.image_in(self._get_template_full_path(), source_image, self.confidence, self.auto_scale,
                                scale)
        elif self.rect is not None:
            res = self.rect_in(self.rect, self.color, source_image, self.confidence)
        else:
            raise RuntimeError(
                "ImageDetection should has either template or rect property, but all are None: {}".format(self))

        if res is None:
            return None
        elif isinstance(res, list):
            results = []
            for one in res:
                result = self._gen_result(one, source_image)
                results.append(result)
            return results
        else:
            return self._gen_result(res, source_image)  # rect是相对偏移量

    def _gen_result(self, res, screen_image):
        result = ImageDetectResult()
        result.rect_on_image = res.rect
        result.rect_on_screen = res.rect.offset_from(self.snapshot)
        result.image = screen_image
        result.scale = res.scale
        self.get_clip(result)
        return result

    def image_in(self, template_file_path, big_image, min_confidence, auto_scale, scale):
        """
        检查两幅图是否相似
        :param min_confidence: 最低可信度, 不足这个可信度的结果将被忽略
        :param template_file_path: 要查找的图文件路径位置
        :param big_image: 大图
        :param auto_scale: 自动缩放模板图，来寻找匹配
        :param scale: 指定要缩放模板图的比例
        :return:相似度，完全相同是1，完全不同是0
        目标图像需要是pillow格式的，将在函数中被转换为opencv格式的，最后用aircv的find_template方法比较是否相似
        """
        if isinstance(big_image, PIL.Image.Image):
            image_current = ActionImage.pil_to_cv(big_image)
        else:
            image_current = big_image

        print('image detection: \r\n\tsnapshot:{}, template:{}'.format(self.snapshot, self.template))

        if self.grayscale:
            image_current = ActionImage.to_grayscale(image_current, high_contrast=True, keep3channel=True)
        if self.to_binary is not None:
            image_current = self.to_binary.convert(image_current)
        ActionImage.log_image('current', image_current, debug=self.debug)

        image_template = ActionImage.load_from_file(template_file_path)
        if self.grayscale:
            image_template = ActionImage.to_grayscale(image_template, high_contrast=True, keep3channel=True)
        if self.to_binary is not None:
            image_template = self.to_binary.convert(image_template)
        ActionImage.log_image('template', image_template, debug=self.debug)

        result_list = ActionImage.find_all_template(image_current, image_template, min_confidence, auto_scale, scale)
        if self.priority is not None:
            for result in result_list:
                if self.priority == "color":
                    rect = result.rect
                    sim = ActionImage.get_color_sim(image_current, self.color, rect.center)
                    result.priority = sim
            result_list.sort(key=lambda x: x.priority, reverse=True)
        if self.debug:
            if result_list is None:
                print('image detection result_list: found None')
            else:
                size = len(result_list)
                print('image detection result_list: found {}'.format(size))
                for index, result in enumerate(result_list):
                    rect = result.rect
                    print('result-{}: confidence-{}, scale-{}, priority-{}， {}'.format(index,
                                                                                       result.confidence if result is not None else None,
                                                                                       result.scale,
                                                                                       result.priority if hasattr(
                                                                                           result,
                                                                                           'priority') else None,
                                                                                       rect if result is not None else None))

                    cv2.rectangle(image_current, (rect.left, rect.top), (rect.right, rect.bottom), (0, 0, 220), 2)
                ActionImage.log_image('result', image_current, debug=self.debug)

        if result_list is None or len(result_list) == 0:
            return None
        elif self.detect_all:
            return result_list
        else:
            return result_list[0]

    def rect_in(self, rect, color, big_image, min_confidence):
        print('image detection: \r\n\tsnapshot:{}, rect:{}， color:{}'.format(self.snapshot, self.rect, self.color))
        result_list = ActionImage.find_rect(big_image, rect, color, find_all=self.detect_all, debug=False)

        if self.debug:
            size = len(result_list)
            print('image detection result_list: found {}'.format(size))
            for index, result in enumerate(result_list):
                res_rect = result.rect
                print('result-{}: top-{}, left-{}'.format(index,
                                                          res_rect.top if result is not None else None,
                                                          res_rect.left if result is not None else None))
                cv2.rectangle(big_image, (res_rect.left, res_rect.top), (res_rect.right, res_rect.bottom),
                              (0, 0, 220), 2)
            ActionImage.log_image('result', big_image, debug=self.debug)
        return result_list

    def get_clip(self, res):
        if self.keep_clip is None:
            return None
        call_env: dict = {'result': res}
        rect = self.keep_clip.call_once(call_env)
        image = res.image
        clip = image[rect.top:rect.bottom, rect.left:rect.right]

        res.clip = clip
        res.clip_on_image = rect
        res.clip_on_screen = res.clip_on_image.offset_from(self.snapshot)

        return clip

    def _get_template_full_path(self):
        if self._template_full_path is not None:
            pass
        elif self.project.path_root is not None:
            self._template_full_path = self.project.path_root + '/' + self.template
        else:
            self._template_full_path = self.template

        return self._template_full_path
