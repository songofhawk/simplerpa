import win32api
import win32con
import win32gui

from simplerpa.core.data import ScreenRect


class ActionWindow:
    screen_width: int = None
    screen_height: int = None

    @classmethod
    def get_current_window(cls):
        """
        获取当前窗口句柄
        Returns:
            int: 当前窗口句柄（hwnd）
        """
        return win32gui.GetForegroundWindow()

    @classmethod
    def set_current_window(cls, hwnd):
        """
        将指定的窗口设置为当前窗口
        Args:
            hwnd (int): 指定的窗口句柄

        Returns:
            None
        """
        if win32gui.IsIconic(hwnd):
            # 如果窗口被最小化了，先恢复
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)

    @classmethod
    def get_window_title(cls, hwnd):
        """
        获取指定窗口标题
        Args:
            hwnd (int): 指定窗口句柄

        Returns:
            str: 窗口标题
        """
        return win32gui.GetWindowText(hwnd)

    @classmethod
    def get_window_class(cls, hwnd):
        """
        获取指定窗口的class name
        Args:
            hwnd (int): 指定窗口句柄

        Returns:
            str: 窗口class name(windows api中的概念，可以看做window系统内部对窗口的标识名）
        """
        return win32gui.GetClassName(hwnd)

    @classmethod
    def get_current_window_title(cls):
        """
        获取当前窗口标题

        Returns:
            str: 窗口标题
        """
        return cls.get_window_title(cls.get_current_window())

    @classmethod
    def find_window(cls, title=None, win_class=None):
        """
        根据窗口的class_name或者标题，查找窗口
        Args:
            title (str): 窗口标题
            win_class (str): 窗口class_name

        Returns:
            int,None: 找到的窗口句柄（hwnd），如果没找到则返回None
        """
        try:
            hwnd = win32gui.FindWindow(win_class, title)
            if hwnd == 0:
                return None
            else:
                return hwnd
        except Exception as ex:
            print('error calling win32gui.FindWindow ' + str(ex))
            return None

    @classmethod
    def get_window_rect(cls, hwnd):
        """
        获取指定窗口的位置和大小
        Args:
            hwnd (int): 指定窗口句柄

        Returns:
            ScreenRect: 窗口的位置和大小
        """
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        return ScreenRect.ScreenRect(left, right, top, bottom)

    @classmethod
    def set_window_pos(cls, hwnd, x, y, width, height):
        """
        设置窗口的位置和大小
        Args:
            hwnd (int): 指定窗口句柄
            x (int): 窗口左上角x坐标
             (int): 窗口左上角y坐标
            width (int): 窗口宽度
            height (int): 窗宽高度

        Returns:

        """
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, width, height, win32con.SWP_SHOWWINDOW)

    @classmethod
    def get_screen_resolution(cls):
        if cls.screen_width is None or cls.screen_height is None:
            cls.refresh_screen_resolution()
        return cls.screen_width, cls.screen_height

    @classmethod
    def refresh_screen_resolution(cls):
        cls.screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        cls.screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
