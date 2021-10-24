class Option:
    project: str = './conf/auto_dingding.yaml'

    def __init__(self, project):
        self.project = project if project is not None else self.project


