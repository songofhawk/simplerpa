class ActionError:
    """
    异常处理相关方法
    """

    @staticmethod
    def trigger(params: tuple):
        """
        主动触发一个运行时异常
        Args:
            params: 要触发的异常内容

        Returns:
            None
        """
        (msg) = params
        # print("ERROR: {}".format(msg))
        raise RuntimeError(msg)

    @staticmethod
    def locate_state(params: tuple):
        """
        这个方法的意思，重新查找当前界面处于哪个状态，但是真正的查找逻辑是在Executor中，这里只是输出一下
        Args:
            params: 定位当前界面所属状态前，要输出的内容

        Returns:
            None
        """
        (msg) = params
        print("ERROR: {}".format(msg))

    @staticmethod
    def level_return(current_state: int):
        """
        这个方法的意思，是退出当前的状态层级，返回上一层，真正的执行逻辑在Executor中，这里只是输出一下
        Args:
            params: 定位当前界面所属状态前，要输出的内容

        Returns:
            None
        """
        print("return to upper level from state: {}".format(current_state))
