from core.action.ActionImage import ActionImage
from core.action.ActionScreen import ActionScreen
from core.data.ScreenRect import ScreenRect
from core.data.StateBlockBase import StateBlockBase
from core.detection.ImageDetection import ImageDetection


class PartSplitter(StateBlockBase):
    start: ImageDetection = None
    end: ImageDetection = None

    def split_parts(self, snapshot, image):
        image_current = image
        if self.start is not None:
            self.start.snapshot = snapshot
            start_found_list = self.start.do_detection(image_current)
        else:
            return None

        start_found_list.sort(key=lambda x: x.rect_on_image.top, reverse=False)

        pre_start_top = None
        parts = []
        for start_found in start_found_list:
            start_top = start_found.rect_on_image.top
            if pre_start_top is not None:
                part = image[pre_start_top:start_top, :]
                parts.append(part)
            pre_start_top = start_top
        return parts


class Extractor(StateBlockBase):
    snapshot: ScreenRect = None
    part_splitter: PartSplitter = None

    def __init__(self):
        self.image = None

    def do(self):
        if self.snapshot is None:
            raise RuntimeError('There should be a "snapshot" attribute in extractor named "{}"!'.format(self.name))

        screen_image = ActionScreen.snapshot(self.snapshot.evaluate())
        image_source = ActionImage.pil_to_cv(screen_image)

        if self.part_splitter is not None:
            image_parts = self.part_splitter.split_parts(self.snapshot, image_source)
            for part in image_parts:
                ActionImage.log_image('part', part)
                self.do_once(part)
        else:
            self.do_once(image_source)

    def do_once(self, image):
        pass
