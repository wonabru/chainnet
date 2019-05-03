import ast
import re

def str2obj(s):
    return ast.literal_eval(s.replace('true', 'True').replace('false', 'False'))


def remove_special_char(in_seq):
	"""
	Function is responsible for normalize strings to defined format (UPPERCASE with '_' replacing any special character)
	:param in_seq: list of strings
	:return: list of strings
	"""
	_sub = re.sub(" {1,3}", "_", in_seq.strip()).upper()
	_chars = ['*', '\\', '&', '/']
	for x in _chars: _sub = _sub.replace(x, '_')
	return _sub


class CFinish:
	finish = False