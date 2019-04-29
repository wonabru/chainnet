from limitedToken import CLimitedToken
from initBlock import CInitBlock
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet
from baseAccount import CBaseAccount
from account import CAccount
from genesis import CGenesis
import ast

class CInitChainnet:
	def __init__(self):

		self.tokens = {}
		self.wallet = CWallet('main')
		self.DB = CSQLLite(self.wallet.pubKey)
		'''
		self.DB.register_node("192.168.56.1")
		self.DB.register_node("10.0.2.2")
		self.DB.register_node("10.0.2.15")
		self.DB.register_node("192.168.0.38")
		self.DB.bootstrapNodes()
		'''
		self.Qcoin = CInitBlock(self.DB, self.wallet)
		_creator = CBaseAccount(self.DB, accountName='creator', address='')
		self.baseToken = CLimitedToken(self.DB, tokenName='Q', totalSupply=self.Qcoin.baseTotalSupply, creator=_creator, address=self.Qcoin.getBaseToken().address, save=False)
		self.baseToken = self.baseToken.copyFromBaseLimitToken(self.Qcoin.getBaseToken())
		self.first_account = self.baseToken.copyFromBaseAccount(self.Qcoin.firstAccount)
		self.first_account.chain.uniqueAccounts[self.baseToken.address] = self.baseToken
		self.add_token(self.baseToken, save=False)
		self.set_my_account()
		self.load_tokens()

	def add_token(self, token, save=True):
		self.tokens[token.address] = token
		if save:
			self.DB.save('tokens', str(list(self.tokens.keys())))
			token.owner.save()
			token.save()

		if self.DB.get(token.address) is None:
			token.save()

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
		try:
			self.first_account.update(with_chain=True)
		except:
			self.first_account.save()

		if self.wallet.pubKey == self.first_account.address:
			self.my_account = self.first_account
		else:
			self.my_account = CAccount(self.DB, 'main', 0, self.wallet.pubKey)
		if self.DB.get(self.my_account.address) is None:
			self.my_account.accountName = 'main'
			self.my_account.save()

	def load_tokens(self):
		self.init_account = self.Qcoin.initAccount
		_my_accounts = self.DB.get('tokens')
		if _my_accounts is None:
			_my_accounts = [self.baseToken.address]
		else:
			_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))
		for acc in _my_accounts:
			try:
				_token = CLimitedToken(self.DB, '__tempInitChainnet__', None, None, acc, False)
				_token.update()
			except:
				try:
					_token = CActionToken(self.DB, '__tempInitChainnet__', None, None, acc, False)
					_token.update()
				except Exception as ex:
					#raise Exception('Load tokens', 'My accounts have token address that there is not in DB')
					_token = self.baseToken if acc == CGenesis().initAccountPubKey else None

			if _token is not None:
				self.tokens[_token.address] = _token

		return True