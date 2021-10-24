class Variable(object):
    def __init__(self):
        self._store_vars = {}
        self._store_index_vars = {}

    def get_vars(self, var_name):
        if var_name not in self._store_vars:
            return None
        return self._store_vars[var_name]

    def set_vars(self, var_name, value):
        self._store_vars[var_name] = value

    def get_index_vars(self, index, var_name=None):
        if index not in self._store_index_vars:
            self._store_index_vars[index] = {}
        var_dict = self._store_index_vars[index]
        if var_name is None:
            return var_dict
        else:
            if not isinstance(var_dict, dict):
                raise RuntimeError('The variable from index "{}" is not a dict, can not be accessed by a var_name "{}"!'.format(index, var_name))

            if var_name in var_dict:
                var_value = var_dict[var_name]
                return var_value
            else:
                raise RuntimeError('The variable from index"{}" with var_name "{}" not found!'.format(index, var_name))

    def set_index_vars(self, index, var_name, value):
        var_dict = self.get_index_vars(index)
        var_dict[var_name] = value
