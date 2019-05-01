import numpy as np
import datetime as dt
from chain import CChain
import ast
from wallet import CWallet
from genesis import CGenesis
from tkinter import messagebox

class CBaseAccount():
	def __init__(self, DB, accountName, address):
		self.kade = DB
		self.decimalPlace = 2
		self.amount = {CGenesis().initAccountPubKey: 0}
		self.address = address
		self.accountName = accountName
		self.chain = CChain()
		self.isLocked = {}
		self.wallet = None
		self.main_account = 0

	def setAmount(self, token, amount, save=True):
		if amount < 0:
			raise Exception('set amount error', 'Amount of tokens cannot be less than zero')
		print('Account: ',self.accountName,' is setting amount ', amount, ' [ ', token.accountName, ' ] ')
		self.amount[token.address] = np.round(amount, self.decimalPlace)

		'''
		if save:
			self.save()
			token.save()
		'''

		return True

	def addAmount(self, token, amount, save=True):

		if token.address not in self.amount.keys():
			self.setAmount(token, 0)
			print('Warning: there was no set any initial amount. Set to 0')

		temp_amount = self.amount[token.address] + amount
		if temp_amount < 0:
			print('not enough funds')
			return False
		return self.setAmount(token, temp_amount, save)

	def load_base_account(self, address):
		try:
			_account = CBaseAccount(self.kade, '__tempInitChainnet__', address)
			_account.update()
		except Exception as ex:
			raise Exception('Load base account', str(ex))

		return  _account

	def lockAccounts(self, account1, signature1, account2address, time_to_close):

		if CWallet().verify('Locking for deal: '+account1.address+' + '+
							account2address+' till '+str(time_to_close),
							signature1, account1.address):
			self.isLocked[account1.address] = account2address
		else:
			raise Exception('Lock Accounts fails. Signature not valid for account '+
							account1.accountName,'Locking for deal fails: '+account1.address+' + '+
							account2address+' till '+str(time_to_close))

		#save means announce to World
		self.save(announce='Lock:'+account1.address+':'+account2address+':')

	def lock_loop(self, account1, account2address, time_to_close):
		self.save(announce='Lock:' + account1.address + ':' + account2address + ':')
		_par = self.kade.look_at('Lock:'+account2address+':'+account1.address+':'+self.address)
		if _par is not None:
			_par = self.verify(_par)
			_token = self.load_base_account(self.address)
			_token.setParameters(_par, with_chain=False)
			if _token is not None and account2address in _token.isLocked.keys() and _token.isLocked[account2address] == account1.address:
				self.isLocked[account2address] = account1.address
				self.save()
				return True

		return False

	def getAmount(self, token):
		return self.amount[token.address]

	def load_wallet(self):
		return CWallet(self.accountName)

	def save_atomic_transaction(self, atomic_transaction, announce=''):
		self.wallet = atomic_transaction.sender.load_wallet()
		_key = atomic_transaction.recipient.address
		_value = atomic_transaction.getParameters()
		_value.append(['Signature', self.wallet.sign(str(_value))])
		#self.verify(_value)
		self.kade.save(announce+_key, _value, announce=announce)

	def save_transaction(self, transaction, announce=''):
		_key = ':Transaction'
		_value = transaction.getParameters()
		self.kade.save(_key, _value, announce=announce)

	def send(self, recipient, token, amount, waiting_time=3600):
		from transaction import CAtomicTransaction, CTransaction
		self.wallet = self.load_wallet()
		time_to_close = dt.datetime.today() + dt.timedelta(seconds=waiting_time)

		atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN', token=token)
		recipient.save_atomic_transaction(atomic, announce='AtomicTransaction:')

		return atomic, time_to_close

	def after_send_loop(self, recipient, atomic, signature, time_to_close):
		from transaction import CTransaction
		self.wallet = self.load_wallet()
		_my_signature = self.wallet.sign(atomic.getHash())
		txn = CTransaction(time_to_close, 1)
		if txn.add(atomic, _my_signature, signature) < 2:
			raise Exception('Error in sending', 'Sending fails. Other fatal error')

		self.save_transaction(txn, announce='FinalTransaction:'+atomic.getHash())
		self.save()
		recipient.save()
		return True

	def send_loop(self, recipient, atomic, time_to_close):
		recipient.save_atomic_transaction(atomic, announce='AtomicTransaction:')
		_signature = self.kade.look_at('SignatureRecipient:' + atomic.getHash())
		if _signature is not None:
			return self.after_send_loop(recipient, atomic, _signature, time_to_close)

		return False

	def process_transaction(self, txn, time_to_close):
		from transaction import CTransaction
		_txn = CTransaction(time_to_close, 1)
		_txn.setParameters(self.kade, txn)
		for i in range(_txn.noAtomicTransactions):
			_atomic = _txn.atomicTransactions[i]
			_sender = _txn.senders[i]
			_recipient = _txn.recipients[i]
			_signSender = _txn.signatures[_sender.address]
			_signRecipient = _txn.signatures[_recipient.address]
			_txn.remove(_atomic,_signSender, _signRecipient)
			_txn.add(_atomic,_signSender, _signRecipient)
			_atomic.token.save()
			_atomic.sender.save()
			_atomic.recipient.save()




	def getParameters(self, with_chain=True):
		_uniqueAccounts, _accountsCreated = self.chain.getParameters()
		if with_chain:
			return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), self.main_account, \
				   str({a: v for a, v in _accountsCreated.items()}), str(list(_uniqueAccounts.keys()))
		else:
			return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), \
					   self.main_account, "{}", "{}"

	def setParameters(self, par, with_chain=True):
		decimalPlace, amount, address, accountName, isLocked, main_account, acc_created, acc_chain = par
		if with_chain:
			_temp_chain = {}
			acc_chain = ast.literal_eval(acc_chain.replace('true', 'True').replace('false', 'False'))
			acc_created = ast.literal_eval(acc_created.replace('true', 'True').replace('false', 'False'))
			for acc in acc_chain:
				_temp_chain[acc] = CBaseAccount(self.kade, '__tempBaseAccount__', acc)
				_temp_chain[acc].update(with_chain=False)
			self.chain.setParameters([acc_created, _temp_chain])

		self.decimalPlace = decimalPlace
		self.amount = amount
		self.address = address
		self.accountName = accountName
		self.main_account = main_account
		self.isLocked = ast.literal_eval(isLocked.replace('true', 'True').replace('false', 'False'))

	def save(self, announce='', count=1):
		_acc_chain, _acc_created = self.chain.getParameters()
		par = [self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), self.main_account,\
			  str(_acc_created), str(list(_acc_chain.keys()))]
		if self.accountName != '' and self.address != '' and self.accountName.find('__') < 0:
			if announce == '':
				announce = 'Account:'
			self.wallet = self.load_wallet()
			if self.wallet.pubKey == self.address:
				par.append(['Signature', self.wallet.sign(str(par))])
				self.verify(par)
			else:
				par.append(['No Signature', ''])
			print('SAVED = ' + str(self.kade.save(self.address, par, announce, count=count)))

	def update(self, with_chain = True):
		_par = self.kade.get(self.address)
		if _par is not None:
			_par = self.verify(_par, local_message=True)
			if _par is not None:
				decimalPlace, amount, address, accountName, isLocked, main_account, _acc_created, _acc_chain = _par
				self.setParameters([decimalPlace, amount, address, accountName, isLocked, main_account,
									_acc_created, _acc_chain], with_chain)
		else:
			self.update_look_at(with_chain=with_chain)


	def verify(self, message, local_message=False):

		_signature = message[-1][1]
		_check = message[-1][0]
		_message = message[:-1]
		if local_message == False and self.address != CGenesis().initAccountPubKey:
			if not CWallet().verify(str(_message), _signature, self.address):
				raise Exception('Verification Fails', 'Message does not have valid signature' + str(message))

			return _message
		else:
			return _message

	def update_look_at(self, with_chain = True):
		_par = self.kade.look_at('Account:'+self.address)
		if _par is not None:
			_par = self.verify(_par)
			if _par is not None:
				decimalPlace, amount, address, accountName, isLocked, main_account, _acc_created, _acc_chain = _par
				self.setParameters([decimalPlace, amount, address, accountName, isLocked, main_account,
									_acc_created, _acc_chain], with_chain)


	def show(self):
		ret = ' ' + self.accountName + ' = ' + str(self.address) + '\n'
		ret += ', '.join(['%s: %.2f' % (key[:5], value) for (key, value) in self.amount.items()])
		ret += '\nAccountsCreated: '
		ret += ', '.join(['%s: %d' % (key[:5], value) for (key, value) in self.chain.accountsCreated.items()])
		ret += '\nUniqueAccounts: '
		ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.chain.uniqueAccounts.items()])
		ret += '\nLockedAccounts: '
		ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.isLocked.items()])
		ret += '\nEnd print'
		print(ret)
		return ret
