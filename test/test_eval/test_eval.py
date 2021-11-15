_call_env = {'print': print}
exp = compile('a = 3', '', 'exec')
exec(exp, {"__builtins__": {}}, _call_env)

exp3 = compile('print(a)', '', 'exec')
exec(exp3, {"__builtins__": {}}, _call_env)

exp2 = compile('a', '', 'eval')
x = eval(exp2, {"__builtins__": {}}, _call_env)
print(x)
