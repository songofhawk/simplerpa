import pyautogui

from simplerpa.core.data.ScreenRect import Vector


def click(x, y=None):
    """
    鼠标点击，可以指定点击的位置
    Args:
        x (int): x坐标
        y (int): y坐标

    Returns:
        None
    """
    if isinstance(x, Vector):
        p = x
        pyautogui.click(p.x, p.y)
    else:
        pyautogui.click(int(x), int(y))


def dbclick(x, y=None):
    """
    鼠标双击，可以指定点击的位置
    Args:
        x (int): x坐标
        y (int): y坐标

    Returns:
        None
    """
    if isinstance(x, Vector):
        p = x
        pyautogui.doubleClick(p.x, p.y)
    else:
        pyautogui.doubleClick(int(x), int(y))


def move(x, y=None):
    """
    移动鼠标指针到指定的位置
    Args:
        x (int): x坐标
        y (int): y坐标

    Returns:
        None
    """
    if isinstance(x, Vector):
        p = x
        pyautogui.moveTo(p.x, p.y)
    else:
        pyautogui.moveTo(int(x), int(y), duration=0.25)


def rightclick(x, y=None):
    """
    鼠标右键点击，可以指定点击的位置
    Args:
        x (int): x坐标
        y (int): y坐标

    Returns:
        None
    """
    if isinstance(x, Vector):
        p = x
        pyautogui.rightClick(p.x, p.y)
    else:
        pyautogui.rightClick(int(x), int(y))


def drag(x, y=None):
    """
    鼠标从当前位置，拖拽到指定的位置
    Args:
        x (int): 目标位置x坐标
        y (int): 目标位置y坐标

    Returns:
        None
    """
    if isinstance(x, Vector):
        p = x
        pyautogui.dragTo(p.x, p.y, 0.5)
    else:
        pyautogui.dragTo(int(x), int(y), 0.5)


def scroll(clicks):
    """
    鼠标滚轮滚动指定的距离
    Args:
        clicks (int): 滚动的格数，正数表示滚动条向上，负数表示滚动条向下

    Returns:
        None
    """
    pyautogui.scroll(clicks)


def position():
    """
    获取鼠标当前位置

    Returns:
        MousePosition对象，有x,y两个属性
    """

    pos = pyautogui.position()
    return Vector(pos[0], pos[1])
