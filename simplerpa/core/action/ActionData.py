import pandas as pd


class ActionData:
    def __init__(self, context):
        self._context = context

    @staticmethod
    def create_dataframe(column_names):
        return pd.DataFrame(columns=column_names)
