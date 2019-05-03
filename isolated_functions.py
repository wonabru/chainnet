import ast
import re
import pickle
from Crypto.PublicKey import RSA
from base64 import b64decode,b64encode
from tkinter import messagebox

def str2obj(s):
    return ast.literal_eval(s.replace('true', 'True').replace('false', 'False'))


def trim_name(name):

	return name.replace('@','').replace('#','')


def remove_special_char(in_seq):
	"""
	Function is responsible for normalize strings to defined format (UPPERCASE with '_' replacing any special character)
	:param in_seq: list of strings
	:return: list of strings
	"""
	_sub = re.sub(" {1,5}", "_", in_seq.strip()).lower()
	_chars = ['*', '\\', '&', '/', '+']
	for x in _chars: _sub = _sub.replace(x, '_')
	return _sub


class CFinish:
	finish = False


def serialize(message):
	return pickle.dumps(message)


def unserialize(ser_message):
	return pickle.loads(ser_message)


def encode(n):
	b = bytearray()
	while n:
		b.append(n & 0xFF)
		n >>= 8
	return b64encode(b).decode('utf-8')


def decode(s):
	b = bytearray(b64decode(s.encode('utf-8')))  # in case you're passing in a bytes/str
	return sum((1 << (bi * 8)) * bb for (bi, bb) in enumerate(b))


class rsa_temp:
	key = RSA.generate(1024)


def showError(ex):
	if len(ex.args) > 1:
		_title, _err = ex.args
	else:
		_title, _err = 'Other error', ex.args
	messagebox.showerror(title=str(_title), message=str(_err))