from typing import Tuple, get_type_hints


class a:
    x: Tuple[int, int] = (5, 19)


clazz_dict = get_type_hints(a)
clazz = clazz_dict['x']
if clazz._name == 'Tuple':
    print('a is a tuple, checked by name')

if hasattr(clazz, '__origin__') and clazz.__origin__ == tuple:
    print('a is a tuple, checked by origin')
