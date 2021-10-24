def select_max(x, y):
    return x if x > y else y


if __name__ == "__main__":
    a = 3
    b = 5
    c = eval('select_max(a , b)')
    print("c is {}".format(c))
