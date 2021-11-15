from ClassA import B,A
from test_import import test2

if __name__ == '__main__':
    b = B()
    A.test = 8
    b.walk()
    test2()
