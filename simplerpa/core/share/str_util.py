import re


# class Expression(object):
#     def __init__(self, param_str):
#         match_result = re.match('\b$(.*?)\b', param_str)
#         if match_result is None:
#             self.has_variable = False
#             self.value = param_str
#         else:
#             self.has_variable = True


def parse_function_call(call_str: str, parse_variable: bool = False):
    left_pos: int = call_str.find('(')
    if left_pos == -1:
        return call_str.strip(), []
    else:
        name: str = call_str[0:left_pos].strip()
        right_pos: int = call_str.rfind(')')
        param_str: str = call_str[left_pos + 1:right_pos].strip()
        params = map(lambda s: s.strip("'") if s.startswith("'") else s,
                     map(str.strip, param_str.split(',')))
        return name, tuple(params)

        # if not parse_variable:
        #     return name, list(params)
        #
        # param_list = []
        # for param in params:
        #     param_list.append(Expression(param))
        # return name, param_list
