import PIL

from simplerpa.core.action.ActionImage import ActionImage
from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.data import Action
from simplerpa.core.data.ScreenRect import ScreenRect
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
    """
    rect_on_image: ScreenRect = None
    rect_on_screen: ScreenRect = None
    image = None
    clip = None
    clip_on_image: ScreenRect = None
    clip_on_screen: ScreenRect = None



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
        confidence (float): 置信度，查找图像的时候，并不需要严格一致，程序会模糊匹配，并返回一个置信度（0 ~ 1之间的一个数值），置信度大于给定的数值，才会认为找到了
        keep_clip (Action.Evaluation): 根据返回结果，额外保持一个截图片段（比如已经查到图像左侧100个像素的区域）

    """
    template: str
    snapshot: ScreenRect
    confidence: float = 0.8
    keep_clip: Action.Evaluation

    def do_detection(self):
        snapshot_image = ActionScreen.snapshot(self.snapshot.evaluate())
        screen_image = ActionImage.pil_to_cv(snapshot_image)
        res = self.image_in(self._get_template_full_path(), screen_image, self.confidence)
        if res is None:
            return None
        if isinstance(res, list):
            results = []
            for one in res:
                result = self._gen_result(one, screen_image)
                results.append(result)
            return results
        else:
            return self._gen_result(res, screen_image)  # rect是相对偏移量

    def _gen_result(self, res, screen_image):
        result = ImageDetectResult()
        result.rect_on_image = res.rect
        result.rect_on_screen = res.rect.offset_from(self.snapshot)
        result.image = screen_image
        self.get_clip(result)
        return result

    def image_in(self, template_file_path, big_image, min_confidence):
        """
        检查两幅图是否相似
        :param min_confidence: 最低可信度, 不足这个可信度的结果将被忽略
        :param template_file_path: 要查找的图文件路径位置
        :param big_image: 大图
        :return:相似度，完全相同是1，完全不同是0
        目标图像需要是pillow格式的，将在函数中被转换为opencv格式的，最后用aircv的find_template方法比较是否相似
        """
        if isinstance(big_image, PIL.Image.Image):
            image_current = ActionImage.pil_to_cv(big_image)
        else:
            image_current = big_image

        ActionImage.log_image('current', image_current, debug=self.debug)
        image_template = ActionImage.load_from_file(template_file_path)
        ActionImage.log_image('template', image_template, debug=self.debug)

        if self.detect_all:
            result_list = ActionImage.find_all_template(image_current, image_template, min_confidence)
            # if self.debug:
            #     for result in result_list:
            #         rect = result.rect
            #         self.log_image('match', image_current[rect.top:rect.bottom, rect.left:rect.right])
            return result_list
        else:
            result = ActionImage.find_one_template(image_current, image_template, min_confidence)
            if self.debug:
                print('image detection result: {}, {}'.format(result.confidence if result is not None else None,
                                                              result.rect if result is not None else None))
            return result

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
