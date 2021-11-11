import cv2

from core.action.ActionImage import ActionImage
from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.action.ActionSystem import ActionSystem
from .Monitor import Monitor
from ..data.ScreenRect import ScreenRect


class ChangeResult(object):
    rate: float = 0
    position: float = None

    def __init__(self, rate, position=None):
        self.rate = rate
        self.position = position


class ImageMonitor(Monitor):
    monitor_diff: bool = True
    snapshot: ScreenRect
    interval: float = 1
    times: int = None
    threshold: float = 0.1
    scroll: str = "up"

    def __init__(self):
        super().__init__()
        self.pre_snapshot = None

    def do(self, source_image=None):
        # if source_image is None:
        #     snapshot_image = ActionScreen.snapshot(self.snapshot.evaluate())
        #     source_image = ActionImage.pil_to_cv(snapshot_image)
        i = 0
        change = None
        rect = self.snapshot.evaluate()
        while self.times is None or i >= self.times:
            change = self._check_change(rect)
            if change is not None:
                break
            if self.debug:
                print("No change, wait...")
            ActionSystem.wait(self.interval)

        if self.debug:
            print("Monitoring change, rate:{}, position:{}".format(change.rate, change.position))
        return change

    def _check_change(self, rect):
        snapshot_image = ActionImage.pil_to_cv(ActionScreen.snapshot(rect))
        if self.pre_snapshot is None:
            self.pre_snapshot = snapshot_image
            return None
        diff = ActionImage.diff(self.pre_snapshot, snapshot_image)

        rate = cv2.countNonZero(diff) / diff.size
        if rate > self.threshold:
            if self.scroll == "up":
                height = self.pre_snapshot.shape[0]
                feature_img = self.pre_snapshot[height - 65:height, :]
            else:
                feature_img = self.pre_snapshot[0:65, :]
            res_list = ActionImage.find_all_template(snapshot_image, feature_img, 0.8)
            if len(res_list) == 0:
                position = None
            else:
                if self.scroll == "up":
                    position = res_list[0].rect.bottom
                else:
                    position = res_list[0].rect.top
            ActionImage.log_image('monitor_pre', self.pre_snapshot)
            ActionImage.log_image('monitor_now', snapshot_image)
            return ChangeResult(rate, position)
        else:
            self.pre_snapshot = snapshot_image
            return None
