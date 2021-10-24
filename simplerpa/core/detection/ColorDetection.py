from typing import Tuple

from simplerpa.core.action.ActionScreen import ActionScreen
from simplerpa.core.detection.Detection import Detection


class ColorDetection(Detection):
    """
    颜色检测，查看当前页面上，指定位置的像素，是否满足指定的颜色值。

    Example:
      ```
      check:
        color:
          pos: (12,92)
          color: (209, 211, 213)
        fail_action: locate_state('当前页面没有检测到指定颜色')
      ```

    Attributes:
        pos (Tuple[int,int]): 像素坐标位置
        color (Tuple[int,int]): rgb表示的颜色值，3组0~255之间的数值
        tolerance (int): 容忍度，rgb三色差绝对值之和，如果小于容忍度，就认为颜色相同
    """
    pos: Tuple[int, int]
    color: Tuple[int, int, int]
    tolerance: int = 0

    def do(self, find_all=False):
        x, y = self.pos
        pix = ActionScreen.pick_color(x, y)
        tolerance = self.tolerance
        r, g, b = pix[:3]
        exR, exG, exB = self.color
        diff = abs(r - exR) + abs(g - exG) + abs(b - exB)

        if self.debug:
            print("检测颜色{}，坐标点({},{}) 颜色{}，与预期颜色({},{},{})差异值‘{}’".format(
                '成功' if diff <= tolerance else '失败',
                x, y,
                pix,
                r, g, b,
                diff
            ))
        if diff <= tolerance:
            return diff
        else:
            return None
