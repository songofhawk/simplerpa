import time


class ActionSystem:
    @classmethod
    def wait(cls, sec):
        """
        暂停
        Returns:
            float: 时间（单位秒）
        """
        time.sleep(sec)

