import datetime as dt
from baseAccount import CBaseAccount
from baseLimitedToken import CBaseLimitedToken
from transaction import CAtomicTransaction, CTransaction
from wallet import CWallet


class CInitBlock():
    def __init__(self, kade, initBlock=None):
        self.kade = kade
        if initBlock is None:
            self.baseTotalSupply = 1000000.00
            self.initAccount = CBaseLimitedToken(self.kade, 'Q', self.baseTotalSupply, address='0')
            self.initAccount.amount[self.initAccount.address] = self.baseTotalSupply
            self.firstAccount = CBaseAccount(self.kade, 'wonabru', address='1')
            try:
                self.update()
            except Exception as ex:
                pass
            _to_save = False
            if self.firstAccount.address == '1':
                self.wallet_first = CWallet('wonabru')
                self.firstAccount.address = self.wallet_first.pubKey
                self.initAccount.chain.uniqueAccounts[str(self.firstAccount.address)] = self.firstAccount
                _to_save = True
            self.initAtomicTransaction = CAtomicTransaction(self.initAccount, self.firstAccount, self.baseTotalSupply, optData='initTransaction', token=self.initAccount)
            self.initTransaction = CTransaction(dt.datetime.today()+dt.timedelta(minutes=1), 1)
            self.initTransaction.add(self.initAtomicTransaction, 'sign_init', 'sign_wonabru', save=False)
            if _to_save: self.save()
        else:
            self.baseTotalSupply = initBlock.baseTotalSupply
            self.initAccount = initBlock.initAccount
            self.firstAccount = initBlock.firstAccount
            self.wallet_first = initBlock.wallet_first
            self.initAtomicTransaction = initBlock.initAtomicTransaction
            self.initTransaction = initBlock.initTransaction

    def getInitTransaction(self):
        return self.initTransaction

    def getBaseToken(self):
        return self.initAccount

    def save(self):
        self.kade.save('initAccount', self.initAccount.getParameters())
        self.kade.save('firstAccount', self.firstAccount.getParameters())
        self.kade.save(self.firstAccount.address, self.firstAccount.getParameters())
        #self.kade.save('initTransaction', self.initTransaction.getParameters())
        
    def update(self):
        self.initAccount.setParameters(self.kade.get('initAccount'))
        self.firstAccount.setParameters(self.kade.get('firstAccount'))
        self.firstAccount.update()
        #self.initTransaction.setParameters(self.kade.get('initTransaction'))
        for acc in self.initAccount.chain.uniqueAccounts.keys():
            if acc not in [self.initAccount.address, self.firstAccount.address]:
                _account = CBaseAccount(self.kade, '__temp__', acc)
                try:
                    _account.update()
                    self.initAccount.chain.uniqueAccounts[acc] = _account
                except Exception as ex:
                    print(str(ex))
                    return False
