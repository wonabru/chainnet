from limitedToken import CLimitedToken
from initBlock import CInitBlock
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet
from baseAccount import CBaseAccount
from account import CAccount
from genesis import CGenesis
from isolated_functions import *
from tkinter import messagebox

class CInitChainnet:
	def __init__(self):

		self.tokens = {}
		self.my_accounts_names = {}
		self.wallet = CWallet('@main')
		#CWallet().saveWallet(CWallet().exportDER(CGenesis().getPrivKey()), CWallet().getPublicKey(CGenesis().getPrivKey()))
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
		else:
			self.my_account = CAccount(self.DB, '@main', 0, self.wallet.pubKey)

		try:
			qcoin_wallet = CWallet(self.baseToken.address)

			if qcoin_wallet is not None:
				self.my_accounts[self.baseToken.address] = {'account': self.baseToken, 'wallet': qcoin_wallet}
		except:
			print('Could not load wallet for Q account')


		if self.DB.get('Account:' + self.my_account.address) is None:
			self.my_account.main_account = 1
			self.my_account.save()

		if not self.check_is_first_account():
			self.baseToken = self.my_account.inviteLimitedToken(self.baseToken.accountName, self.baseToken.creator,
											   					self.baseToken.address, save=False)
			self.baseToken.save(announce='EXTERNAL')

		self.my_accounts[self.my_account.address] = {'account': self.my_account, 'wallet': self.wallet}
		self.DB.save('my_main_accounts', str(list(set(self.my_accounts.keys()))))

	def get_external_addresses(self):

		_external_accounts = self.DB.get('EXTERNAL')

		if _external_accounts is not None:
			return _external_accounts
		else:
			return []

	def get_tokens_addresses(self):
		_my_accounts = self.DB.get('tokens')
		if _my_accounts is None:
			_my_accounts = [self.baseToken.address]
		else:
			_my_accounts = str2obj(_my_accounts)

		return _my_accounts

	def get_my_accounts(self):
		_my_accounts = self.DB.get('my_main_accounts')
		if _my_accounts is None:
			_my_accounts = list(self.my_accounts.keys())
		else:
			_my_accounts = str2obj(_my_accounts)

		return list(set(_my_accounts + self.get_external_addresses() + self.get_tokens_addresses()))

	def select_my_acount_by_name(self, name, update=True):

		if update: self.update_my_accounts()

		for add, acc in self.my_accounts.items():
			if acc['account'].accountName == name.split(':')[0]:
				return acc['account']
		return None

	def select_my_acount_by_address(self, address, update=True):

		if update: self.update_my_accounts()

		for add, acc in self.my_accounts.items():
			if acc['account'].address== address:
				return acc['account']
		return None

	def load_tokens(self):
		self.init_account = self.Qcoin.initAccount
		_my_accounts = self.get_tokens_addresses()
		for acc in _my_accounts:
			try:
				_token = CLimitedToken(self.DB, '?', None, None, acc)
				_token.load_wallet()
				_token.update()
			except:
				try:
					_token = CActionToken(self.DB, '?', None, None, acc)
					_token.load_wallet()
					_token.update()
				except Exception as ex:
					_token = self.baseToken if acc == CGenesis().initAccountPubKey else None
					_token.load_wallet()

			if _token is not None:
				self.tokens[_token.address] = _token

		return True

	def get_my_accounts_names(self):
		return self.my_accounts_names.values()


	def update_my_accounts(self):
		self.load_tokens()
		try:
			self.init_account = self.Qcoin.initAccount

			_my_accounts = self.get_my_accounts()
			for acc in _my_accounts:
				if acc in self.tokens.keys():

					self.my_accounts[acc] = {'account': self.tokens[acc], 'wallet': self.tokens[acc].wallet}
					self.my_accounts_names[acc] = self.tokens[acc].accountName
				else:
					_account = CAccount(self.DB, '?', None, acc)
					try:
						_account.load_wallet()
						_account.update(with_chain=True)

						self.my_accounts[_account.address] = {'account': _account, 'wallet': _account.wallet}
						self.my_accounts_names[_account.address] = _account.accountName
					except Exception as ex:
						showError(ex)

			_temp_my_main_account = self.select_my_acount_by_name(self.my_account.accountName, update=False)
			self.my_account = _temp_my_main_account if _temp_my_main_account is not None else self.my_account
		except Exception as ex:
			print('No database found', str(ex))