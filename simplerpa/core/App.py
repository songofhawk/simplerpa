from simplerpa.core.Option import Option
from simplerpa.core.ProjectLoader import ProjectLoader
from simplerpa.core.Executor import Executor
from simplerpa.core.data.Project import Project


class App:
    option: Option = None
    project: Project = None

    def __init__(self, option: Option):
        self.option = option
        self.load_project(option.project)

    def load_project(self, project_file: str):
        self.project = ProjectLoader.load(project_file)

    def execute(self):
        executor = Executor(self.project)
        executor.run()
