import re

from ruamel.yaml import yaml_object

from simplerpa.core.action import ActionWindow
from simplerpa.core.data import Action
from simplerpa.core.share.yaml import yaml


@yaml_object(yaml)
class Vector(object):
    yaml_tag = u'!vector'

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def offset_rect(self, x, y, width, height):
        """
        按照x,y偏移左上角位置，
        按照width, height改变矩形框大小
        """
        left = self.x + x
        top = self.y + y
        right = left + width
        bottom = top + height
        return ScreenRect(left, right, top, bottom)

    def offset(self, x, y):
        """
        大小不变，位置偏移一段距离
        """
        return Vector(self.x + x, self.y + y)

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            'x:{}, y:{}'.format(node.x, node.y))

    @classmethod
    def from_yaml(cls, constructor, node):
        result = re.search(r"x:(\S*)\s*,\s*y:(\S*)\s*", node.value)
        if result is None:
            raise RuntimeError('ScreenRect string is not formatted well: ""!'.format(node.value))
        else:
            v = result.groups()
            v = list(map(int, v))
            # splits = node.value.split(', ')
            # test = list(map(lambda x: x + '_sss', splits))
            # v = list(map(lambda x: int(x[1]) if x[1].isdigit() else x[1], map(methodcaller("split", ":"), splits)))
            # print(v)
            return cls(x=v[0], y=v[1])


@yaml_object(yaml)
class ScreenRect(object):
    yaml_tag = u'!rect'
    snapshot = None

    def __init__(self, left=None, right=None, top=None, bottom=None):
        # super(ScreenRect, self).__init__([left, right, top, bottom])
        # self._inner_list = [left, right, top, bottom]
        self.has_exp = False
        self.exp = None
        if isinstance(left, str):
            self.has_exp = True
            self.left = None
            if right is None and top is None and bottom is None:
                # 如果只有第一个参数，其他参数都没有传，说明整个字符串，是一个ScreenRect表达式
                self.exp = Action.Evaluation(left)
                self._exp_str = left
            else:
                self.left_exp: Action.Evaluation = Action.Evaluation(left)
        else:
            self.left = left
            self.left_exp = None

        if isinstance(right, str):
            self.has_exp = True
            self.right_exp: Action.Evaluation = Action.Evaluation(right)
            self.right = None
        else:
            self.right = right
            self.right_exp = None

        if isinstance(top, str):
            self.has_exp = True
            self.top_exp: Action.Evaluation = Action.Evaluation(top)
            self.top = None
        else:
            self.top = top
            self.top_exp = None

        if isinstance(bottom, str):
            self.has_exp = True
            self.bottom_exp: Action.Evaluation = Action.Evaluation(bottom)
            self.bottom = None
        else:
            self.bottom = bottom
            self.bottom_exp = None

        self.center_x = 0
        self.center_y = 0
        if not self.has_exp:
            self._compute()

    def _compute(self):
        self.center_x = (self.left + self.right) // 2
        self.center_y = (self.top + self.bottom) // 2
        self.center = Vector(self.center_x, self.center_y)

    def evaluate(self):
        if not self.has_exp:
            return self

        if self.exp is not None:
            temp_rect = self.exp.evaluate_exp()
            self.left = temp_rect.left
            self.right = temp_rect.right
            self.top = temp_rect.top
            self.bottom = temp_rect.bottom
            self._compute()
            return self

        if self.left_exp is not None:
            self.left = self.left_exp.evaluate_exp()
        if self.right_exp is not None:
            self.right = self.right_exp.evaluate_exp()
        if self.top_exp is not None:
            self.top = self.top_exp.evaluate_exp()
        if self.bottom_exp is not None:
            self.bottom = self.bottom_exp.evaluate_exp()

        self._compute()
        return self

    def swap_top_bottom(self):
        temp_top = self.top
        screen_width, screen_height = ActionWindow.ActionWindow.get_screen_resolution()
        top = screen_height - temp_top if temp_top < screen_height else 0
        bottom = screen_height - self.bottom if self.bottom < screen_height else 0
        return ScreenRect(self.left, self.right, top, bottom)

    @classmethod
    def center_expand(cls, width, height):
        screen_width, screen_height = ActionWindow.ActionWindow.get_screen_resolution()
        left = (screen_width - width) / 2
        right = screen_width - left
        top = (screen_height - height) / 2
        bottom = screen_height - top
        return ScreenRect(left, right, top, bottom)

    def __str__(self):
        return 'l:{},  r:{},  t:{},  b:{}'.format(self.left, self.right, self.top, self.bottom)

    @classmethod
    def to_yaml(cls, representer, node):
        return representer.represent_scalar(cls.yaml_tag,
                                            'l:{}, r:{}, t:{}, b:{}'.format(node.left, node.right, node.top,
                                                                            node.bottom))
        # return {'l': self.left, 'r': self.right, 't': self.top, 'b': self.bottom}

    @classmethod
    def from_yaml(cls, constructor, node):
        result = re.search(r"l:(\S*)\s*,\s*r:(\S*)\s*,\s*t:(\S*)\s*,\s*b:(\S*)", node.value)
        if result is None:
            raise RuntimeError('ScreenRect string is not formatted well: ""!'.format(node.value))
        else:
            v = result.groups()
            v = list(map(int, v))
            # splits = node.value.split(', ')
            # test = list(map(lambda x: x + '_sss', splits))
            # v = list(map(lambda x: int(x[1]) if x[1].isdigit() else x[1], map(methodcaller("split", ":"), splits)))
            # print(v)
            return cls(left=v[0], right=v[1], top=v[2], bottom=v[3])

    def offset_from(self, other_rect):
        if (isinstance(self.left, float) or isinstance(self.left, int)) \
                and (isinstance(other_rect.left, float) or isinstance(other_rect.left, int)):
            left = self.left + other_rect.left
        else:
            raise RuntimeError("left must be an integer or float number for '+' operator")
        if (isinstance(self.top, float) or isinstance(self.top, int)) \
                and (isinstance(other_rect.top, float) or isinstance(other_rect.top, int)):
            top = self.top + other_rect.top
        else:
            raise RuntimeError("top must be an integer or float number for '+' operator")

        if (isinstance(self.right, float) or isinstance(self.right, int)) \
                and (isinstance(other_rect.left, float) or isinstance(other_rect.left, int)):
            right = self.right + other_rect.left
        else:
            raise RuntimeError("right must be an integer or float number for '+' operator")
        if (isinstance(self.bottom, float) or isinstance(self.bottom, int)) \
                and (isinstance(other_rect.top, float) or isinstance(other_rect.top, int)):
            bottom = self.bottom + other_rect.top
        else:
            raise RuntimeError("bottom must be an integer or float number for '+' operator")

        return ScreenRect(left, right, top, bottom)

    def snap_left(self, width, height=None):
        if height is not None:
            offset_y = (height - (self.bottom - self.top)) / 2
        else:
            offset_y = 0

        return ScreenRect(self.left - width, self.top - offset_y, self.bottom + offset_y)

    def snap_right(self, width, height=None):
        if height is not None:
            offset_y = (height - (self.bottom - self.top)) / 2
        else:
            offset_y = 0

        return ScreenRect(self.right, self.right + width, self.top - offset_y, self.bottom + offset_y)

    def snap_top(self, height):
        return ScreenRect(self.left, self.right, self.top - height, self.top)

    def snap_bottom(self, height):
        return ScreenRect(self.left, self.right, self.bottom, self.bottom + height)

    @property
    def topleft(self):
        return Vector(self.left, self.top)
