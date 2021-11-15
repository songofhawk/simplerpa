import pandas as pd


class ActionData:
    def __init__(self, context):
        self._context = context

    @staticmethod
    def create_dataframe(column_names):
        if isinstance(column_names,list):
            return pd.DataFrame(columns=column_names)
        else:
            return pd.DataFrame()
