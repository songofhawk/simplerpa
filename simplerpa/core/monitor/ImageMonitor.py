import cv2

from simplerpa.core.action.ActionImage import ActionImage
from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.action.ActionSystem import ActionSystem
from .Monitor import Monitor
from ..const import MONITOR_RESULT
from ..data.Action import Action
from ..data.ScreenRect import ScreenRect


class ChangeResult(object):
    rate: float = 0
    position: float = None
    scroll: str = None

    def __init__(self, rate, position=None, scroll=None):
        self.rate = rate
        self.position = position


class ImageMonitor(Monitor):
    monitor_diff: bool = True
    snapshot: ScreenRect
    interval: float = 1
    times: int = None
    threshold: float = 0.1

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
        while self.times is None or i < self.times:
            change = self._check_change(rect)
            if change is not None:
                break
            if self.debug:
                print("No change, wait...")
                # ActionImage.log_image('monitor_pre_snapshot', self.pre_snapshot, self.debug)
            ActionSystem.wait(self.interval)
            i += 1
        if self.debug:
            print("Monitoring change, rate:{}, position:{}".format(change.rate, change.position))
        Action.save_call_env({MONITOR_RESULT: change})

        return change

    def _check_change(self, rect):
        snapshot_image = ActionImage.pil_to_cv(ActionScreen.snapshot(rect))
        if self.pre_snapshot is None:
            self.pre_snapshot = snapshot_image
            return None
        diff = ActionImage.diff(self.pre_snapshot, snapshot_image)

        rate = cv2.countNonZero(diff) / diff.size
        if rate > self.threshold:
            ActionImage.log_image('monitor_pre', self.pre_snapshot, self.debug)
            # 等半秒，以防消息连续发送
            ActionSystem.wait(0.5)
            scroll = "up"
            height = self.pre_snapshot.shape[0]
            feature_img = self.pre_snapshot[height - 65:height, :]
            res_list = ActionImage.find_all_template(snapshot_image, feature_img, 0.8)

            if len(res_list) == 0:
                scroll = 'down'
                feature_img = self.pre_snapshot[0:65, :]
                res_list = ActionImage.find_all_template(snapshot_image, feature_img, 0.8)

            if len(res_list) == 0:
                position = None
            else:
                if scroll == "up":
                    position = res_list[0].rect.bottom
                else:
                    position = res_list[0].rect.top

            ActionImage.log_image('monitor_now', snapshot_image, self.debug)
            self.pre_snapshot = None
            return ChangeResult(rate, position, scroll)
        else:
            self.pre_snapshot = snapshot_image
            return None
