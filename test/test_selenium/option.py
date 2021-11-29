class Option:
    SPLITTER: str = '/'

    def __init__(self, output_dir: str = '.', result_file: str = 'result.csv', limit: int = 100):
        self.output_dir = output_dir + self.SPLITTER
        self.result_file = result_file if result_file is not None else self.result_file
        self.output_result = self.output_dir + self.result_file

        self.limit = limit
