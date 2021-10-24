import win32api
import pyautogui as autogui

from simplerpa.core.action.ActionImage import ActionImage


class ActionScreen:
    @staticmethod
    def change_resolution(params: tuple):
        """
        改变屏幕分辨率
        Args:
            params (Tuple[int,int]): 指定分辨率的宽和高

        Returns:
            None
        """
        (width, height) = params
        dm = win32api.EnumDisplaySettings(None, 0)
        dm.PelsWidth = width
        dm.PelsHeight = height
        dm.BitsPerPel = 32
        dm.DisplayFixedOutput = 1  # 0:缺省; 1:居中; 2:拉伸
        win32api.ChangeDisplaySettings(dm, 0)

    @classmethod
    def snapshot(cls, rect):
        """
        根据跟定的ScreenRect区域截图
        Args:
            rect: 遵从一般系统坐标系的矩形区域(左上角为0,0点), autogui和Pillow都适用

        Returns:
            返回PIL格式的指定区域截图
        """
        screen_shot = autogui.screenshot()
        # rect = rect.swap_top_bottom()
        crop_img = screen_shot.crop(
            (int(float(rect.left)), int(float(rect.top)), int(float(rect.right)), int(float(rect.bottom))))
        return crop_img

    @classmethod
    def snapshot_cv(cls, rect):
        """
        根据跟定的ScreenRect区域截图
        Args:
            rect: 遵从一般系统坐标系的矩形区域(左上角为0,0点), autogui和opencv都适用

        Returns:
            返回opencv格式的指定区域截图
        """
        pil_image = cls.snapshot(rect)
        return ActionImage.pil_to_cv(pil_image)

    @staticmethod
    def pick_color(x, y):
        """
        获取屏幕上指定位置像素的颜色
        Args:
            x: 指定位置x坐标
            y: 指定位置y坐标

        Returns:
            List[int]: 长度为4的整形数组，分别用0~255之间的数字，表示R,G,B,A四个通道
        """
        return autogui.pixel(x, y)

    @staticmethod
    def pixel_matches_color(x, y, color_tuple, tolerance=0):
        """
        检查给定的颜色和屏幕上特定坐标点的颜色是否匹配
        Args:
            x: 指定位置x坐标
            y: 指定位置y坐标
            color_tuple (Tuple[int]): (R,G,B) 组成的颜色值
            tolerance: 容忍度

        Returns:
            bool: 是否匹配
        """
        return autogui.pixelMatchesColor(x, y, color_tuple, tolerance)
