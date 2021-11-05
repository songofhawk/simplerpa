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
        if self.start is None and self.end is None:
            print("start and end template are all none in splitter '{}'".format(self.name))
            return

        start_found_list = None
        if self.start is not None:
            self.start.snapshot = snapshot
            start_found_list = self.start.do_detection(image_current)
            if start_found_list is None:
                print("start template not found in splitter '{}'".format(self.name))
        if start_found_list is not None:
            start_found_list.sort(key=lambda x: x.rect_on_image.top, reverse=False)

        end_found_list = None
        if self.end is not None:
            self.end.snapshot = snapshot
            end_found_list = self.end.do_detection(image_current)
            if end_found_list is None:
                print("end template not found in splitter '{}'".format(self.name))
        if end_found_list is not None:
            end_found_list.sort(key=lambda x: x.rect_on_image.top, reverse=False)

        pre_top = None
        pre_bottom = None
        parts = []
        if self.start is not None and self.end is None:
            for start_found in start_found_list:
                start_top = start_found.rect_on_image.top
                if pre_top is not None:
                    part = image[pre_top:start_top, :]
                    parts.append(part)
                pre_top = start_top
        elif self.start is None and self.end is not None:
            for end_found in end_found_list:
                end_bottom = end_found.rect_on_image.bottom
                if pre_bottom is not None:
                    part = image[pre_bottom:end_bottom, :]
                    parts.append(part)
                pre_bottom = end_bottom
        else:
            start_len = len(start_found_list)
            end_len = len(end_found_list)
            count = min(start_len, end_len)
            for i in range(count):
                start_top = start_found_list[i].rect_on_image.top if self.start is not None else None
                end_bottom = end_found_list[i].rect_on_image.bottom if self.end is not None else None
                if start_top < end_bottom:
                    part = image[start_top:end_bottom, :]
                    parts.append(part)
                else:
                    if pre_top is not None:
                        part = image[pre_top:end_bottom, :]
                        parts.append(part)
                    pre_top = start_top
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
            for index, part in enumerate(image_parts):
                ActionImage.log_image('part-{}'.format(index), part)
                self.do_once(part)
        else:
            self.do_once(image_source)

    def do_once(self, image):
        pass
