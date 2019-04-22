import numpy as np
import datetime as dt
from transaction import CAtomicTransaction, CTransaction
from limitedToken import CLimitedToken
from initBlock import CInitBlock
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet
from baseAccount import CBaseAccount


class CInitChainnet:
	def __init__(self):
		self.tokens = {}
		self.wallet = CWallet(False)
		self.DB = CSQLLite(self.wallet.pubKey)
		self.Qcoin = CInitBlock(self.DB)
		_creator = CBaseAccount(self.DB, accountName='0', address=-1)
		self.baseToken = CLimitedToken(self.DB, tokenName='Q', totalSupply=1, creator=_creator, address=0)
		self.baseToken = self.baseToken.copyFromBaseLimitToken(self.Qcoin.getBaseToken())
		self.first_account = self.baseToken.copyFromBaseAccount(self.Qcoin.firstAccount)
		self.add_token(self.baseToken)
		self.set_my_account()

	def add_token(self, account):
		self.tokens[account.address] = account

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