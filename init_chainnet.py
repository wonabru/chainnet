import numpy as np
import datetime as dt
from transaction import CAtomicTransaction, CTransaction
from limitedToken import CLimitedToken
from initBlock import CInitBlock
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet
from baseAccount import CBaseAccount
from account import CAccount
import ast

class CInitChainnet:
	def __init__(self):
		self.tokens = {}
		self.wallet = CWallet('main')
		self.DB = CSQLLite(self.wallet.pubKey)
		self.Qcoin = CInitBlock(self.DB)
		_creator = CBaseAccount(self.DB, accountName='0', address='-1')
		self.baseToken = CLimitedToken(self.DB, tokenName='Q', totalSupply=self.Qcoin.baseTotalSupply, creator=_creator, address=self.Qcoin.getBaseToken().address, save=False)
		self.baseToken = self.baseToken.copyFromBaseLimitToken(self.Qcoin.getBaseToken())
		self.first_account = self.baseToken.copyFromBaseAccount(self.Qcoin.firstAccount)
		self.add_token(self.baseToken, save=False)
		self.set_my_account()
		self.load_tokens()

	def add_token(self, token, save=True):
		self.tokens[token.address] = token
		if save:
			self.DB.save('tokens', str(list(self.tokens.keys())))
		token.save()
		token.owner.save()

	def get_token(self, address):
		return self.tokens[address]

	def get_token_by_name(self, name):
		for key, token in self.tokens.items():
			if token.accountName == name:
				return token
		return None

	def check_is_first_account(self):
		return True if self.first_account.address == self.wallet.pubKey else False

	def set_my_account(self):
		self.my_account = self.first_account

	def load_tokens(self):
		self.init_account = self.Qcoin.initAccount
		_my_accounts = self.DB.get('tokens')
		if _my_accounts is None:
			_my_accounts = [self.baseToken.address]
		else:
			_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))
		for acc in _my_accounts:
			try:
				_token = CLimitedToken(self.DB, '__temp__', None, None, acc, False)
				_token.update()
			except:
				try:
					_token = CActionToken(self.DB, '__temp__', None, None, acc, False)
					_token.update()
				except Exception as ex:
					print(str(ex))
					_token = self.baseToken if acc == '0' else None

			if _token is not None:
				self.tokens[_token.address] = _token

		return True