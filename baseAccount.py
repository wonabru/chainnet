import numpy as np
import datetime as dt
from chain import CChain
import ast
from wallet import CWallet
from genesis import CGenesis
import time

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

    def setAmount(self, token, amount, save=True):
        if amount < 0:
            print('Amount of tokens cannot be less than zero')
            return False
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
            print('Attach first please')
            return False
        
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
            self.isLocked[account2address] = account1.address
        else:
            raise Exception('Lock Accounts fails. Signature not valid for account '+
                            account1.accountName,'Locking for deal fails: '+account1.address+' + '+
                                                  account2address+' till '+str(time_to_close))

        #save means announce to World
        self.save(announce='Lock:')

        while dt.datetime.today() < time_to_close:
            _par = self.kade.look_at('Lock:'+self.address)
            if _par is not None:
                print(str(_par))
                _token = self.load_base_account(self.address)
                _token.setParameters(_par, with_chain=False)
                if _token is not None and account1.address in _token.isLocked.keys() and _token.isLocked[account1.address] == account2address:
                    self.isLocked[account1.address] = account2address
                    self.save()
                    break
                if time_to_close < dt.datetime.today():
                    raise Exception('Lock Accounts fails', 'Could not found locked accounts till '+str(time_to_close))
            time.sleep(1)

    def getAmount(self, token):
        return self.amount[token.address]

    def load_wallet(self):
        if self.wallet is None:
            return CWallet(self.accountName)
        else:
            return self.wallet

    def save_atomic_transaction(self, atomic_transaction, announce=''):
        _key = atomic_transaction.recipient.address
        _value = atomic_transaction.getParameters()
        self.kade.save(_key, _value, announce=announce)

    def save_transaction(self, transaction, announce=''):
        _key = transaction.getHash()
        _value = transaction.getParameters()
        self.kade.save(_key, _value, announce=announce)

    def send(self, recipient, token, amount, waiting_time=3600):
        from transaction import CAtomicTransaction, CTransaction
        self.wallet = self.load_wallet()
        time_to_close = dt.datetime.today() + dt.timedelta(seconds=waiting_time)

        atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN', token=token)
        self.save_atomic_transaction(atomic, announce='AtomicTransaction:')

        _signature = None
        while dt.datetime.today() < time_to_close:
            _signature = self.kade.look_at('SignatureRecipient:'+atomic.getHash())
            if _signature is not None:
                break
            if time_to_close < dt.datetime.today():
                raise Exception('Sign Transaction fails', 'Could not obtain valid signature from recipient till '+str(time_to_close))
            time.sleep(0.1)

        self.wallet = self.load_wallet()
        _my_signature = self.wallet.sign(atomic.getHash())
        txn = CTransaction(time_to_close, 1)
        if txn.add(atomic, _my_signature, _signature) < 2:
            raise Exception('Error in sending', 'Sending fails. Other fatal error')

        self.save_transaction(txn)
        self.save()
        recipient.save()

        return True

    def getParameters(self, with_chain=True):
        _uniqueAccounts, _accountsCreated = self.chain.getParameters()
        if with_chain:
            return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), \
                   str({a: v for a, v in _accountsCreated.items()}), str(list(_uniqueAccounts.keys()))
        else:
            return self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), "{}", "{}"

    def setParameters(self, par, with_chain=True):
        decimalPlace, amount, address, accountName, isLocked, acc_created, acc_chain = par
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
        self.isLocked = ast.literal_eval(isLocked.replace('true', 'True').replace('false', 'False'))


    def save(self, announce=''):
        _acc_chain, _acc_created = self.chain.getParameters()
        par = self.decimalPlace, self.amount, self.address, self.accountName, str(self.isLocked), str(_acc_created), str(list(_acc_chain.keys()))
        if self.accountName != '' and self.address != '':
            print('SAVED = ' + str(self.kade.save(self.address, par, announce)))
        else:
            pass
        '''
        for acc in _acc_chain:
            _account = self.chain.uniqueAccounts[acc]
            results = self.kade.get(acc)
            if results is None and acc != self.address and _account is not None:
                _account.save()
        '''

    def update(self, with_chain = True):
	    _par = self.kade.get(self.address)
	    if _par is not None:
	        decimalPlace, amount, address, accountName, isLocked, _acc_created, _acc_chain = _par
	        self.setParameters([decimalPlace, amount, address, accountName, isLocked, _acc_created, _acc_chain], with_chain)

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
