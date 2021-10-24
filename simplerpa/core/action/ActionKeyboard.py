import pyautogui


class ActionKeyboard:
    """键盘操作

    """
    @staticmethod
    def hotkey(*keys):
        """
        发送热键
        Examples:
            ```python
            action: hotkey("ctrl","c")
            ```
            ```python
            action: hotkey("alt","tab")
            ```
        Args:
            *keys: 热键组合，多键组合用多个参数表示

        Returns:
            None

        """
        pyautogui.hotkey(*keys)

    @staticmethod
    def type(str_to_type, interval=0):
        """
        把指定字符串以键盘敲击的形式输入
        Args:
            str_to_type (str): 要输入的字符串
            interval (float): 每个输入字符之间的时间间隔，单位是秒

        Returns:
            None
        """
        if interval == 0:
            pyautogui.write(str_to_type)
        else:
            pyautogui.write(str_to_type, interval)

    @staticmethod
    def press(key_or_keys, interval=0):
        """
        点击特定的键
        Args:
            key_or_keys (str,List[str]): 表示键的字符串或者字符串数组
            interval (float): 第一个参数是数组，那么这里表示多个敲击之间的时间间隔，单位是秒

        Returns:

        """
        if interval == 0:
            pyautogui.press(key_or_keys)
        else:
            pyautogui.press(key_or_keys, interval)
