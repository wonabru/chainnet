import ast

def str2obj(s):
    return ast.literal_eval(s.replace('true', 'True').replace('false', 'False'))


class CFinish:
	finish = False