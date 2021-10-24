from operator import methodcaller

from ruamel.yaml import yaml_object

from simplerpa.core.data import Action
from simplerpa.core.share.yaml import yaml


class ScreenPoint(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def offset_rect(self, x, y, width, height):
        left = self.x + x
        top = self.y + y
        right = left + width
        bottom = top + height
        return ScreenRect(left, right, top, bottom)

    def offset(self, x, y):
        return ScreenPoint(self.x + x, self.y + y)


@yaml_object(yaml)
class ScreenRect(object):
    yaml_tag = u'!rect'
    snapshot = None

    # screen_width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
    # screen_height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

    def __init__(self, left=None, right=None, top=None, bottom=None):
        # super(ScreenRect, self).__init__([left, right, top, bottom])
        # self._inner_list = [left, right, top, bottom]
        self.has_exp = False
        if isinstance(left, str):
            self.has_exp = True
            self.left_exp: Action.Evaluation = Action.Evaluation(left)
            self.left = None
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
        self.center_x = (self.left + self.right) / 2
        self.center_y = (self.top + self.bottom) / 2

    def evaluate(self):
        if not self.has_exp:
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
        top = self.screen_height - temp_top if temp_top < self.screen_height else 0
        bottom = self.screen_height - self.bottom if self.bottom < self.screen_height else 0
        return ScreenRect(self.left, self.right, top, bottom)

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
        splits = node.value.split(', ')
        # test = list(map(lambda x: x + '_sss', splits))
        v = list(map(lambda x: int(x[1]) if x[1].isdigit() else x[1], map(methodcaller("split", ":"), splits)))
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
            raise RuntimeError("left must be an integer or float number for '+' operator")
        if (isinstance(self.bottom, float) or isinstance(self.bottom, int)) \
                and (isinstance(other_rect.top, float) or isinstance(other_rect.top, int)):
            bottom = self.bottom + other_rect.top
        else:
            raise RuntimeError("top must be an integer or float number for '+' operator")

        return ScreenRect(left, right, top, bottom)

    def snap_left(self, width):
        return ScreenRect(self.left - width, self.left, self.top, self.bottom)

    def snap_bottom(self, height):
        return ScreenRect(self.left, self.right, self.bottom, self.bottom + height)

    @property
    def topleft(self):
        return ScreenPoint(self.left, self.top)
