from core.detection.ImageDetection import ImageDetection

from .Extractor import Extractor


class FormExtractor(Extractor):
    def __init__(self):
        super().__init__()

    def do(self):
        parts = self.split_parts()
