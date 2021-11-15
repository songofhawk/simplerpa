class A:
    test = 5


class B(A):
    def walk(self):
        print(A.test)


class C(A):
    def walk(self):
        print(A.test)
