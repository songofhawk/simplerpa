import pyperclip


class ActionClipboard:
    """
    剪贴板相关操作
    """
    @classmethod
    def copy(cls, str_to_copy):
        """
        复制指定字符串到剪贴板
        Args:
            str_to_copy: 要复制的字符串

        Returns:
            None
        """
        pyperclip.copy(str_to_copy)

    @classmethod
    def paste(cls):
        """
        提取当前剪贴板中的文本，作为字符串返回
        Returns:
            str: 当前剪贴板中的文本字符串
        """
        pyperclip.paste()
