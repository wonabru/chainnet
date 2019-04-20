import numpy as np
import datetime as dt
from chain import CChain


class CBaseAccount():
    def __init__(self, accountName = ''):
        self.minAmount = 0.01
        self.amount = 0
        self.address = np.random.randint(1,1000000000)
        if accountName == '':
            self.accountName = str(self.address)
        else:
            self.accountName = accountName

        self.chain = CChain()
   
    def setAmount(self, amount):
        if amount < 0:
            return False
        self.amount = amount
        self.amount = np.round(self.amount / self.minAmount) * self.minAmount
        return True

    def addAmount(self, amount):
        self.amount += amount
        if self.amount < 0:
            return False
        self.amount = np.round(self.amount / self.minAmount) * self.minAmount
        return True
    
    def getAmount(self):
        return self.amount
    
    def send(self, recipient, amount):
        from transaction import CAtomicTransaction, CTransaction
        
        atomic = CAtomicTransaction(self, recipient, amount, optData='Simple TXN')
        txn = CTransaction(dt.datetime.today()+dt.timedelta(1), 1)
        if txn.add(atomic, 'sign_1', 'sign_2') == True:
            print('Current amount of Q on ', self.accountName, ' = ', self.amount)
            print('Current amount of Q on', recipient.accountName, ' = ', recipient.amount)
            
