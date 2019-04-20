import numpy as np
import datetime as dt
from baseAccount import CBaseAccount
from baseLimitedToken import CBaseLimitedToken
from transaction import CAtomicTransaction, CTransaction

class CInitBlock():
    def __init__(self):
        self.initAccount = CBaseLimitedToken('Q', 1000000.00)
        self.initAccount.address = 0
        self.firstAccount = CBaseAccount('wonabru')
        self.firstAccount.address = 1
        self.initAtomicTransaction = CAtomicTransaction(self.initAccount, self.firstAccount, 1000000.00, optData='initTransaction')
        self.initTransaction = CTransaction(dt.datetime.strptime('2019-03-24', '%Y-%m-%d'), 1)
        self.initTransaction.add(self.initAtomicTransaction, 'sign_init', 'sign_wonabru')
        
    def getInitTransaction(self):
        return self.initTransaction