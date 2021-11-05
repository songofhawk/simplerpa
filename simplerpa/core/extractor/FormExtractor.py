from typing import Tuple, List

from core.detection.ImageDetection import ImageDetection

from .Extractor import Extractor
from ..action.ActionImage import ActionImage


class FormExtractor(Extractor):
    foreground: Tuple[int, int, int] = (0, 0, 0)
    tolerance: float = 0.01
    field_def: List[Tuple[str, str]] = None

    def __init__(self):
        super().__init__()

    def do_once(self, image):
        ActionImage.find_content_parts(image, )
