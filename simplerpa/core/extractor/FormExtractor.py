from typing import Tuple, List

from core.detection.ImageDetection import ImageDetection

from .Extractor import Extractor
from ..action.ActionImage import ActionImage
from ..data.Action import Evaluation, Action
from ..data.StateBlockBase import StateBlockBase


class FormField(StateBlockBase):
    name: str = None
    feature: ImageDetection = None
    position: Evaluation = None
    foreground: Tuple[int, int, int] = (0, 0, 0)
    background: Tuple[int, int, int] = (255, 255, 255)
    tolerance: float = 0.1

    def __init__(self):
        self.content = None

    def get_content(self, image):
        result = self.feature.do_detection(image)
        if result is None:
            raise RuntimeError('field "{}" not found!'.format(self.name))
        rect = Action.call_once(self.position, {'feature_rect': result.rect_on_image})
        content_img = image[rect.top:rect.bottom, rect.left:rect.right]
        ActionImage.log_image('field_{}_content'.format(self.name), content_img, debug=self.debug)
        main_part, main_part_bin = ActionImage.find_main_part(content_img, self.foreground, self.tolerance)
        ActionImage.log_image('field_{}_main_part'.format(self.name), main_part, debug=self.debug)
        rows_img = ActionImage.split_rows(main_part_bin, 255)
        # 这里已经是二值图像了，所以背景颜色一定是255（只能取0和255两种颜色）
        content = ""
        for row_img in rows_img:
            ActionImage.log_image('field_{}_main_part'.format(self.name), row_img, debug=self.debug)
            row_txt = ActionImage.ocr(row_img)
            content += row_txt
        return content


class FormExtractor(Extractor):
    foreground: Tuple[int, int, int] = (0, 0, 0)
    tolerance: float = 0.1
    fields: List[FormField] = None

    def __init__(self):
        super().__init__()

    def do_once(self, image):
        # pass
        for field in self.fields:
            content = field.get_content(image)
            print("{}: {}".format(field.name, content))
        fields = ActionImage.find_content_parts(image, self.foreground, self.tolerance)
