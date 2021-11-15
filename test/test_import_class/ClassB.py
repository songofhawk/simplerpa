from ClassA import A


class B(A):
    def walk(self):
        A.test = 8
        print(A.test)
