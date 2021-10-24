def test():
    print('I am a function')


class A:
    fun_dict = {
        'test': test
    }

    def __init__(self):
        self.attr1 = 'xxx'
        self.func = test
        # self.func = A.fun_dict['test']
        pass

    def call(self):
        self.func()


if __name__ == '__main__':
    a = A()
    a.call()
