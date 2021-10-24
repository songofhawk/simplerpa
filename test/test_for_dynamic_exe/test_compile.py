exp = compile('select_max(a , b)', '', 'eval')


def select_max(x, y):
    return x if x > y else y


if __name__ == "__main__":
    for i in range(10):
        a = i
        b = i + 10
        c = eval(exp)
        print("c is {}".format(c))
