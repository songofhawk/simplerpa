class Option:
    SPLITTER: str = '/'
    output_dir: str = '.'
    result_file: str = 'result.csv'
    limit: int = 100

    def __init__(self, output_dir: str, result_file: str, limit: int):
        # 这里不用参数缺省值，是为了简化调用方，不需要非空判断
        self.output_dir = output_dir + self.SPLITTER if output_dir is not None else self.output_dir + self.SPLITTER
        self.result_file = result_file if result_file is not None else self.result_file
        self.output_result = self.output_dir + self.result_file

        self.limit = limit if limit is not None else self.limit
