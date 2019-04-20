import datetime as dt
from baseAccount import CBaseAccount
from baseLimitedToken import CBaseLimitedToken
from transaction import CAtomicTransaction, CTransaction


class CInitBlock():
    def __init__(self, kade):
        self.kade = kade
        self.baseTotalSupply = 1000000.00
        self.initAccount = CBaseLimitedToken(self.kade, 'Q', self.baseTotalSupply)
        self.initAccount.address = 0
        self.initAccount.setAmount(self.initAccount, self.baseTotalSupply)
        self.firstAccount = CBaseAccount(self.kade, 'wonabru')
        self.firstAccount.address = 1
        self.initAtomicTransaction = CAtomicTransaction(self.initAccount, self.firstAccount, self.baseTotalSupply, optData='initTransaction', token=self.initAccount)
        self.initTransaction = CTransaction(dt.datetime.today()+dt.timedelta(minutes=1), 1)
        self.initTransaction.add(self.initAtomicTransaction, 'sign_init', 'sign_wonabru')
        self.initAccount.chain.uniqueAccounts[self.firstAccount.address] = self.firstAccount
        self.save()

    def getInitTransaction(self):
        return self.initTransaction

    def getBaseToken(self):
        return self.initAccount

    def save(self):
        self.kade.save('initAccount', self.initAccount.getParameters())
        self.kade.save('firstAccount', self.firstAccount.getParameters())
        '''
        self.kade.save('initTransaction', self.initTransaction.getParameters())
        
    def update(self):
        self.initAccount.setParameters(self.kade.get('initAccount'))
        self.firstAccount.setParameters(self.kade.get('firstAccount'))
        self.initTransaction.setParameters(self.kade.get('initTransaction'))    
        for acc in self.initAccount.chain.uniqueAccounts.values():
            if acc not in [self.initAccount, self.firstAccount]:
                acc.update()
        '''