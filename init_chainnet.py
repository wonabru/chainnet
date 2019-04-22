import numpy as np
import datetime as dt
from transaction import CAtomicTransaction, CTransaction
from limitedToken import CLimitedToken
from initBlock import CInitBlock
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet



class CInitChainnet:
	def __init__(self):
		self.tokens = {}
		self.wallet = CWallet()
		self.DB = CSQLLite(self.wallet.pubKey)
		self.Qcoin = CInitBlock(self.DB)
		self.baseToken = CLimitedToken(self.DB, 'Q', 1, 0)
		self.baseToken = self.baseToken.copyFromBaseLimitToken(self.Qcoin.getBaseToken())
		self.first_account = self.baseToken.copyFromBaseAccount(self.Qcoin.firstAccount)
		self.add_token(self.baseToken)

	def add_token(self, account):
		self.tokens[account.address] = account

	def check_is_first_account(self):
		return True if self.first_account.address == self.wallet.pubKey else False
