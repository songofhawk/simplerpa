class ActionDo:
    def __init__(self, context):
        self._context = context

    def do(self, params):
        raise NotImplementedError("'do' method should be implemented by sub class!")
