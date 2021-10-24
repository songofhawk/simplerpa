def pr(x):
    print('My result: {}'.format(x))


if __name__ == "__main__":
    s = '''
a = 15
b = 3
if a > b:
    pr(a+b)
'''
    exec(s)
