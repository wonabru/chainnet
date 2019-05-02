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
		self.DB = CSQLLite()

		self.Qcoin = CInitBlock(self.DB)
		_creator = CBaseAccount(self.DB, accountName='creator', address='')
		self.baseToken = CLimitedToken(self.DB, tokenName='Q', totalSupply=self.Qcoin.baseTotalSupply,
									   creator=_creator, address=self.Qcoin.getBaseToken().address)

		self.baseToken = self.baseToken.copyFromBaseLimitToken(self.Qcoin.getBaseToken())
		self.first_account = self.baseToken.copyFromBaseAccount(self.Qcoin.firstAccount)
		self.first_account.chain.uniqueAccounts[self.baseToken.address] = self.baseToken
		self.add_token(self.baseToken, save=False)
		self.my_accounts = {}
		self.set_my_account()
		self.load_tokens()
		self.baseToken = self.tokens[self.baseToken.address]

	def add_token(self, token, save=True):
		self.tokens[token.address] = token
		if save:
			self.DB.save('tokens', str(list(self.tokens.keys())))
			token.owner.save()
			token.save()

		if self.DB.get('Account:' + token.address) is None:
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

		if self.check_is_first_account():
			self.my_account = self.first_account
			self.my_accounts[self.baseToken.address] = {'account': self.baseToken, 'wallet': CGenesis().getPrivKey()}
		else:
			self.my_account = CAccount(self.DB, 'main', 0, self.wallet.pubKey)

		if self.DB.get(self.my_account.address) is None:
			self.my_account.main_account = 1
			self.my_account.save()

		self.my_accounts[self.my_account.address] = {'account': self.my_account, 'wallet': self.wallet}
		self.DB.save('my_main_accounts', str(list(set(self.my_accounts.keys()))))

	def get_external_addresses(self):
		_external_accounts = self.DB.get('EXTERNAL')
		if _external_accounts is not None:
			#_external_accounts = ast.literal_eval(_external_accounts.replace('true', 'True').replace('false', 'False'))
			return _external_accounts
		else:
			return []

	def get_tokens_addresses(self):
		_my_accounts = self.DB.get('tokens')
		if _my_accounts is None:
			_my_accounts = [self.baseToken.address]
		else:
			_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))

		return _my_accounts

	def get_my_accounts(self):
		_my_accounts = self.DB.get('my_main_accounts')
		if _my_accounts is None:
			_my_accounts = list(self.my_accounts.keys())
		else:
			_my_accounts = ast.literal_eval(_my_accounts.replace('true', 'True').replace('false', 'False'))

		return list(set(_my_accounts + self.get_external_addresses() + self.get_tokens_addresses()))

	def load_tokens(self):
		self.init_account = self.Qcoin.initAccount
		_my_accounts = self.get_tokens_addresses()
		for acc in _my_accounts:
			try:
				_token = CLimitedToken(self.DB, '__tempInitChainnet__', None, None, acc)
				_token.update()
			except:
				try:
					_token = CActionToken(self.DB, '__tempInitChainnet__', None, None, acc)
					_token.update()
				except Exception as ex:
					_token = self.baseToken if acc == CGenesis().initAccountPubKey else None

			if _token is not None:
				self.tokens[_token.address] = _token

		return True