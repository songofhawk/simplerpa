import time

import win32con
import win32gui


def get_current_window():
    return win32gui.GetForegroundWindow()


def set_current_window(hwnd):
    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)


def get_window_title(hwnd):
    return win32gui.GetWindowText(hwnd)


def get_current_window_title():
    return get_window_title(get_current_window())


def find_window_by_title(title):
    try:
        return win32gui.FindWindow(None, title)
    except Exception as ex:
        print('error calling win32gui.FindWindow ' + str(ex))
        return -1


def set_window_pos(hwnd, x, y, width, height):
    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, x, y, width, height, win32con.SWP_SHOWWINDOW)


if __name__ == "__main__":
    # 获取当前窗口句柄(是一个整数)
    print(get_current_window())
    # 获取当前窗口标题
    print(get_current_window_title())

    # 给定一个标题, 查找这个窗口, 如果找到就放到最前
    hwnd = find_window_by_title('文档')
    set_current_window(hwnd)
    time.sleep(2)
    set_window_pos(hwnd, 0, 0, 1024, 768)
    # 打印刚刚切换到最前的窗口标题
    print(get_current_window_title())

# https://www.programcreek.com/python/example/89828/win32gui.SetForegroundWindow
#     def find_window_movetop(cls):
#         hwnd = win32gui.FindWindow(None, cls.processname)
#         win32gui.ShowWindow(hwnd, 5)
#         win32gui.SetForegroundWindow(hwnd)
#         rect = win32gui.GetWindowRect(hwnd)
#         sleep(0.2)
#         return rect
