import numpy as np
import datetime as dt
from chain import CChain

class CBaseAccount():
    def __init__(self, DB, accountName = '', wallet = None):
        self.kade = DB
        self.decimalPlace = 2
        self.amount = {0: 0}
        if wallet is not None:
            self.address = wallet.pubKey
        else:
            self.address = np.random.randint(1, 100000000)
        if accountName == '':
            self.accountName = str(self.address)[:5]
        else:
            self.accountName = accountName

        self.chain = CChain()
        self.isLocked = {}
   
    def setAmount(self, token, amount):
        if amount < 0:
            print('Amount of tokens cannot be less than zero')
            return False
        self.amount[token.address] = np.round(amount, self.decimalPlace)
        return True

    def addAmount(self, token, amount):
        
        if token.address not in self.amount.keys():
            self.amount[token.address] = 0
        
        temp_amount = self.amount[token.address] + amount
        if temp_amount < 0:
            print('not enough funds')
            return False
        self.amount[token.address] = np.round(temp_amount, self.decimalPlace)
        return True
    
    def lockAccounts(self, sender, recipient):
        self.isLocked[sender.address] = recipient.address
        self.isLocked[recipient.address] = sender.address
        #save means announce to World
        self.save()
        
    def getAmount(self, token):
        return self.amount[token.address]
    
    def send(self, recipient, token, amount):
        from transaction import CAtomicTransaction, CTransaction
        
        token.lockAccounts(self, recipient)
        
        atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN', token=token)
        txn = CTransaction(dt.datetime.today()+dt.timedelta(seconds=10), 1)
        if txn.add(atomic, 'sign_1', 'sign_2') == False:
            print('Sending fails')
            return False

        return True

    def getParameters(self):
        return self.decimalPlace, self.amount, self.address, self.accountName

    def setParameters(self, decimalPlace, amount, address, accountName):
        self.decimalPlace = decimalPlace
        self.amount = amount
        self.address = address
        self.accountName = accountName

    def save(self):
        self.kade.save(self.address, self.getParameters())
        
        
    def update(self):
        decimalPlace, amount, address, accountName = self.kade.get(self.address)
        self.setParameters(decimalPlace, amount, address, accountName)

    def show(self):
        ret = ' ' + self.accountName + ' = ' + str(self.address) + ' '
        ret += ', '.join(['%d: %.2f' % (key, value) for (key, value) in self.amount.items()])
        ret += '\nAccountsCreated: '
        ret += ', '.join(['%d: %d' % (key, value) for (key, value) in self.chain.accountsCreated.items()])
        ret += '\nEnd print'
        print(ret)
        return ret
