import inspect
from typing import get_type_hints, TypeVar


class DataObject(object):
    pass


def get_type_definition(obj):
    types_in_class = get_type_hints(type(obj))
    instance_in_obj = obj.__dict__
    for k, v in instance_in_obj.items():
        types_in_class[k] = type(v)

    # 这里有个合并两个字典的方法，要求python >= 3.5
    # types = {**types_in_class, **types_in_obj}
    return types_in_class


def has_init_argument(clazz):
    signature = inspect.signature(clazz.__init__)
    for name, parameter in signature.parameters.items():
        # print(clazz.__name__, name, parameter.default, parameter.annotation, parameter.kind)
        if name not in ['self', 'args', 'kwargs']:
            return True
    return False


def _parse_tuple_str(tuple_str):
    striped_str = tuple_str.strip()
    if striped_str.startswith('(') and striped_str.endswith(')'):
        return eval(striped_str, {"__builtins__": {}}, {})
    else:
        raise RuntimeError('需要的项目')


T = TypeVar('T')


def from_dict_list(dict_list_obj, clazz: T, reserve_extra_attr=True, init_empty_attr=True, reserved_classes=None) -> T:
    if clazz is None and not reserve_extra_attr:
        return None

    if reserved_classes is not None and clazz in reserved_classes:
        return dict_list_obj

    elif isinstance(dict_list_obj, list):
        new_list = []
        if clazz is None:
            item_type = None
        elif hasattr(clazz, '__origin__'):
            # __origin__ 是泛型对应的原始类型，比如list或是dict
            item_type = clazz.__args__[0]
            # __args__ 是泛型参数数组，对于list来说，它只有一个元素，表示了list中保存的是什么类型的数据，如果是dict，它应该有两个参数，分别表示key和value的数据类型
            # 这里获取了list中应当保存的数据类型
        else:
            # 之前考虑预期类型应该和实际类型匹配，也就是'class.__origin__ is list'，
            # 但为了更灵活一些，有些节点是既可以是类实例，也可以是该实例组成的数组的，比如check节点
            # 所以改成了即使预期定义不是list，这里也按list解析
            item_type = clazz

        for item in dict_list_obj:
            typed_obj = from_dict_list(item, item_type, reserve_extra_attr, init_empty_attr, reserved_classes)
            if typed_obj is not None:
                new_list.append(typed_obj)
        return new_list

    elif isinstance(dict_list_obj, dict):
        if has_init_argument(clazz):
            raise TypeError('类 {} 的构造函数需要参数，无法通过dict实例化！\r\n {}'.format(clazz.__name__, dict_list_obj))
        if clazz is None:
            obj = DataObject()
            types = None
        else:
            clazz = find_sub_class(dict_list_obj, clazz)
            # 如果定义的类包含子类，那么根据dict中的key来推断使用哪个子类
            obj = clazz()
            types = get_type_definition(obj)

        for k, v in dict_list_obj.items():
            if types is not None and k in types:
                attr_type = types[k]
            else:
                attr_type = None
            typed_obj = from_dict_list(v, attr_type, reserve_extra_attr, init_empty_attr, reserved_classes)
            if typed_obj is not None:
                setattr(obj, k, typed_obj)

        '''初始化那些在types中存在，dict_list数据中没有属性'''
        if init_empty_attr and types is not None:
            for k in types.keys():
                if k not in dict_list_obj and not hasattr(obj, k):
                    # 注意一下，如果有个属性在构造函数中初始化了，它也会在types中存在
                    setattr(obj, k, None)

        return obj
    elif is_basic_type(dict_list_obj):
        if clazz is None:
            return dict_list_obj
        elif type(dict_list_obj) == clazz:
            return dict_list_obj
        elif hasattr(clazz, '__origin__') and clazz.__origin__ == tuple and isinstance(dict_list_obj, str):
            return _parse_tuple_str(dict_list_obj)
        else:
            # 如果dict_list_obj是个基本类型(比如字符串),但对应的是定义clazz一个类, 那么假设该类的构造函数, 正好接收这个类的参数
            return clazz(dict_list_obj)
    else:
        # raise TypeError('需要转换的对象，是一个出乎意料的类型：{}，\n\r{}'.format(type(yaml_obj), yaml_obj))
        # 对于实现了from_yaml的类，可以直接得到对象实例
        return dict_list_obj


def is_basic_type(obj):
    if isinstance(obj, str) or \
            isinstance(obj, int) or isinstance(obj, float) or isinstance(obj, bool) or isinstance(obj, complex):
        return True
    else:
        return False


def to_dict_list(obj):
    if isinstance(obj, list):
        list1 = []
        for item in obj:
            list1.append(to_dict_list(item))
        return list1
    elif isinstance(obj, dict):
        dict1 = {}
        for k, v in obj.items():
            dict1[k] = to_dict_list(v)
    elif is_basic_type(obj):
        return obj
    else:
        dict1 = {}
        for k, v in obj.__dict__.items():
            dict1[k] = to_dict_list(v)
        return dict1


def find_sub_class(dict_obj, clazz):
    sub_list = clazz.__subclasses__()
    if sub_list is None or len(sub_list) == 0:
        return clazz
    got_the_clazz = True
    sub_clazz = None
    for sub_clazz in sub_list:
        for k in dict_obj.keys():
            if k not in sub_clazz:
                got_the_clazz = False
                break
        if not got_the_clazz:
            continue
        break
    if got_the_clazz:
        return sub_clazz
    else:
        return clazz
