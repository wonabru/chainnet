import numpy as np
import datetime as dt
from chain import CChain
from wallet import CWallet
from genesis import CGenesis
from transaction import CTransaction, CAtomicTransaction
from isolated_functions import *

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

	def setAmount(self, token, amount):
		if amount < 0:
			raise Exception('set amount error', 'Amount of tokens cannot be less than zero')
		print('Account: ',self.accountName,' is setting amount ', amount, ' [ ', token.accountName, ' ] ')
		self.amount[token.address] = np.round(amount, self.decimalPlace)

		return True

	def addAmount(self, token, amount):

		if token.address not in self.amount.keys():
			self.setAmount(token, 0)
			print('Warning: there was no set any initial amount. Set to 0')

		temp_amount = self.amount[token.address] + amount
		if temp_amount < 0:
			print('not enough funds')
			return False
		return self.setAmount(token, temp_amount)

	def load_base_account(self, address):
		try:
			_account = CBaseAccount(self.kade, '?', address)
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
		self.save(announce='Lock:'+account1.address+':'+account2address+':', who_is_signing=account1)

	def lock_loop(self, account1, account2address, time_to_close, finish):

		self.save(announce='Lock:' + account1.address + ':' + account2address + ':', who_is_signing=account1)
		_par = self.kade.look_at('Lock:'+account2address+':'+account1.address+':'+self.address)
		if _par is not None:
			_par = self.verify(_par, account2address)
			_token = self.load_base_account(self.address)
			_token.setParameters(_par, with_chain=2)
			if _token is not None and account1.address in _token.isLocked.keys()\
					and _token.isLocked[account1.address] == account2address and \
					_token.isLocked[account2address] == account1.address:
				self.isLocked[account2address] = account1.address
				self.save()
				finish.finish = True
				return

		finish.finish = False

	def getAmount(self, token):
		return self.amount[token.address]

	def load_wallet(self):
		try:
			self.wallet = CWallet(self.address)
		except Exception as ex:
			print('load wallet', 'could not found wallet: '+str(ex))

	def save_atomic_transaction(self, atomic_transaction, announce=''):
		atomic_transaction.sender.load_wallet()
		_key = atomic_transaction.recipient.address
		_value = atomic_transaction.getParameters()
		_value.append(['Signature', atomic_transaction.sender.wallet.sign(str(_value))])

		self.kade.save(announce+_key, _value, announce=announce)

	def save_transaction(self, transaction, announce=''):
		_key = ':Transaction'
		_value = transaction.getParameters()
		self.kade.save(_key, _value, announce=announce)

	def send(self, recipient, token, amount, waiting_time=3600):
		from transaction import CAtomicTransaction
		self.load_wallet()
		time_to_close = dt.datetime.today() + dt.timedelta(seconds=waiting_time)

		atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN', token=token)
		recipient.save_atomic_transaction(atomic, announce='AtomicTransaction:')

		return atomic, time_to_close

	def send_loop(self, recipient, atomic, time_to_close, finish):
		recipient.save_atomic_transaction(atomic, announce='AtomicTransaction:')
		_signature = self.kade.look_at('SignatureRecipient:' + atomic.getHash())
		if _signature is not None:
			self.after_send_loop(recipient, atomic, _signature, time_to_close)
			finish.finish = True
			return

		finish.finish = False

	def after_send_loop(self, recipient, atomic, signature, time_to_close):
		from transaction import CTransaction
		self.load_wallet()
		_my_signature = self.wallet.sign(atomic.getHash())
		txn = CTransaction(time_to_close, 1)

		if self.chain.check_transaction_to_add(txn.check_add_return_hash(atomic, _my_signature, signature)):

			if txn.add(atomic, _my_signature, signature) < 2:
				raise Exception('Error in sending', 'Sending fails. Other fatal error')

			self.chain.addTransaction(txn)
			self.save_transaction(txn, announce='FinalTransaction:'+atomic.getHash())
			self.save()
			recipient.save()
		else:
			print('Transaction is just on place')

	def process_transaction(self, txn, time_to_close, atomicTransactions_list):
		_txn = CTransaction(time_to_close, 1)
		_txn.setParameters(self.kade, txn)
		for i in range(_txn.noAtomicTransactions):
			_atomic = _txn.atomicTransactions[i]
			_atomic = CAtomicTransaction(atomicTransactions_list[i].sender, atomicTransactions_list[i].recipient,
										 _atomic.amount, _atomic.optData, atomicTransactions_list[i].token, _atomic.time)
			_sender = _txn.senders[i]
			_recipient = _txn.recipients[i]
			_signSender = _txn.signatures[_sender.address]
			_signRecipient = _txn.signatures[_recipient.address]
			_txn.remove_atomic_for_addresses(_signSender, _signRecipient, _sender.address, _recipient.address)
			_txn.add(_atomic,_signSender, _signRecipient)
			_atomic.token.chain.addTransaction(_txn)
			_atomic.sender.chain.addTransaction(_txn)
			_atomic.recipient.chain.addTransaction(_txn)
			_atomic.token.save()
			_atomic.sender.save()
			_atomic.recipient.save()

	def getParameters(self, with_chain=1):
		_uniqueAccounts, _accountsCreated, _transactions = self.chain.getParameters()
		if with_chain:
			return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), self.main_account, \
				   str({a: v for a, v in _accountsCreated.items()}), str(list(_uniqueAccounts.keys())), \
				   str({a: v for a, v in _transactions.items()})
		else:
			return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), \
					   self.main_account, "{}", "{}", "{}"

	def setParameters(self, par, with_chain=1):
		decimalPlace, amount, address, accountName, isLocked, main_account, acc_created, acc_chain, transactions = par
		if with_chain:
			with_chain -= 1
			if with_chain <= 0: with_chain = 0

			acc_chain = str2obj(acc_chain)
			acc_created = str2obj(acc_created)
			transactions = str2obj(transactions)

			_temp_chain = {}
			for acc in acc_chain:
				_temp_chain[acc] = CBaseAccount(self.kade, '?', acc)
				_temp_chain[acc].update(with_chain=with_chain)

			_temp_transactions = {}
			for txn in transactions:
				_tx = CTransaction(dt.datetime.today(), 1)
				par = self.kade.get('txn:' + txn)
				_tx.setParameters(self.kade, par)
				_temp_transactions[_tx.getHash()] = _tx
			self.chain.setParameters([acc_created, _temp_chain, _temp_transactions])

		self.decimalPlace = decimalPlace
		self.amount = amount
		self.address = address
		self.accountName = accountName
		self.main_account = main_account
		self.isLocked = str2obj(isLocked)

	def save(self, announce='', who_is_signing=None):
		_acc_chain, _acc_created, _transactions = self.chain.getParameters()

		self.save_transactions(_transactions)

		par = [self.decimalPlace, self.amount, self.address, self.accountName.replace('@','').replace('#',''), str(self.isLocked),
			   self.main_account, str(_acc_created), str(list(_acc_chain.keys())), str(list(_transactions.keys()))]

		if self.accountName != '' and self.address != '' and self.accountName.find('?') < 0:
			if announce == '':
				announce = 'Account:'

			if who_is_signing is None:
				self.load_wallet()
				who_is_signing = self

			try:
				par.append(['Signature', who_is_signing.wallet.sign(str(par))])
				self.verify(par, who_is_signing.address)
				print('SAVED = ' + str(self.kade.save(self.address, par, announce)))
			except:
				print('SAVED NO SIGN = ' + str(self.kade.save(self.address, self.address, announce='EXTERNAL')))
				print('No signature','wrong wallet was load')

	def save_transactions(self, transactions):

		for _key, tx in transactions.items():
			_value = tx.getParameters()
			self.kade.save(_key, _value, 'txn:')

	def update(self, with_chain = 2):
		_par = self.kade.get('Account:' + self.address)

		if _par is not None:
			_par = self.verify(_par, self.address)
			if _par is not None:
				decimalPlace, amount, address, accountName, isLocked, main_account, _acc_created, _acc_chain, _txn = _par

				self.setParameters([decimalPlace, amount, address, '@'+accountName, isLocked, main_account,
									_acc_created, _acc_chain, _txn], with_chain)

		else:
			with_chain -= 1
			if with_chain <= 0: with_chain = 0
			self.update_look_at(with_chain=with_chain)

	def update_look_at(self, with_chain = True):
		_par = self.kade.look_at('Account:'+self.address)
		if _par is not None:
			_par = self.verify(_par, self.address)
			if _par is not None:
				decimalPlace, amount, address, accountName, isLocked, main_account, _acc_created, _acc_chain, _txn = _par
				self.setParameters([decimalPlace, amount, address, '#'+accountName, isLocked, main_account,
									_acc_created, _acc_chain, _txn], with_chain)

	def verify(self, message, address):

		_signature = message[-1][1]
		_check = message[-1][0]
		_message = message[:-1]

		if not CWallet().verify(str(_message), _signature, address):
			raise Exception('Verification Fails', 'Message does not have valid signature' + str(message))

		return _message

	def show(self):
		ret = ' ' + self.accountName + ' = ' + str(self.address) + '\n'
		ret += ', '.join(['%s: %.2f' % (key[:5], value) for (key, value) in self.amount.items()])
		ret += '\nAccountsCreated: '
		ret += ', '.join(['%s: %d' % (key[:5], value) for (key, value) in self.chain.accountsCreated.items()])
		ret += '\nUniqueAccounts: '
		ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.chain.uniqueAccounts.items()])
		ret += '\nLockedAccounts: '
		ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.isLocked.items()])
		ret += '\nTransactions: '
		ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.chain.transactions.items()])
		ret += '\nEnd print'
		print(ret)
		return ret
