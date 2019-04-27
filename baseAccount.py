import numpy as np
import datetime as dt
from chain import CChain
import ast
from wallet import CWallet

class CBaseAccount():
    def __init__(self, DB, accountName, address):
        self.kade = DB
        self.decimalPlace = 2
        self.amount = {'0': 0}
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

    
    def lockAccounts(self, sender, recipient):
        self.isLocked[sender.address] = recipient.address
        self.isLocked[recipient.address] = sender.address
        #save means announce to World
        self.save()
        
    def getAmount(self, token):
        return self.amount[token.address]

    def load_wallet(self):
        if self.wallet is None:
            return CWallet(self.accountName)
        else:
            return self.wallet

    def send(self, recipient, token, amount):
        from transaction import CAtomicTransaction, CTransaction
        
        token.lockAccounts(self, recipient)
        
        atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN', token=token)
        self.wallet = self.load_wallet()
        _my_signature = self.wallet.sign(atomic.getHash())
        txn = CTransaction(dt.datetime.today()+dt.timedelta(seconds=1000), 1)
        if txn.add(atomic, _my_signature, '__future__') < 2:
            print('Sending fails')
            return False

        self.save()
        recipient.save()

        return True

    def getParameters(self, with_chain=True):
        _uniqueAccounts, _accountsCreated = self.chain.getParameters()
        if with_chain:
            return self.decimalPlace, self.amount, self.address, self.accountName, \
                   str({a: v for a, v in _accountsCreated.items()}), str(list(_uniqueAccounts.keys()))
        else:
            return self.decimalPlace, self.amount, self.address, self.accountName, "{}", "{}"

    def setParameters(self, par, with_chain=True):
        decimalPlace, amount, address, accountName, acc_created, acc_chain = par
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


    def save(self):
        _acc_chain, _acc_created = self.chain.getParameters()
        par = self.decimalPlace, self.amount, self.address, self.accountName, str(_acc_created), str(list(_acc_chain.keys()))
        if self.accountName != '' and self.address != '':
            print('BEFORE = ' + str(par))
            print('AFTER = ' + str(self.kade.save(self.address, par)))
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
        decimalPlace, amount, address, accountName, _acc_created, _acc_chain = self.kade.get(self.address)
        self.setParameters([decimalPlace, amount, address, accountName, _acc_created, _acc_chain], with_chain)

    def show(self):
        ret = ' ' + self.accountName + ' = ' + str(self.address) + '\n'
        ret += ', '.join(['%s: %.2f' % (key[:5], value) for (key, value) in self.amount.items()])
        ret += '\nAccountsCreated: '
        ret += ', '.join(['%s: %d' % (key[:5], value) for (key, value) in self.chain.accountsCreated.items()])
        ret += '\nUniqueAccounts: '
        ret += ', '.join(['%s' % (key[:5]) for (key, value) in self.chain.uniqueAccounts.items()])
        ret += '\nEnd print'
        print(ret)
        return ret
