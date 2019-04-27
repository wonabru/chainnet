import datetime as dt
from baseAccount import CBaseAccount
from baseLimitedToken import CBaseLimitedToken
from transaction import CAtomicTransaction, CTransaction
from wallet import CWallet

initBlock = None

class CInitBlock():
    def __init__(self, kade=None):
        global initBlock

        if initBlock is None:
            self.kade = kade
            self.baseTotalSupply = 1000000.00
            self.initAccount = CBaseLimitedToken(self.kade, 'Q', self.baseTotalSupply, address='0')
            self.initAccount.amount[self.initAccount.address] = self.baseTotalSupply
            self.firstAccount = CBaseAccount(self.kade, 'wonabru', address='1')
            self.wallet_first = CWallet('wonabru')
            self.firstAccount.address = self.wallet_first.pubKey
            self.initAccount.chain.uniqueAccounts[self.firstAccount.address] = self.firstAccount
            self.firstAccount.chain.uniqueAccounts[self.initAccount.address] = self.initAccount
            self.initAtomicTransaction = CAtomicTransaction(self.initAccount, self.firstAccount, self.baseTotalSupply, optData='initTransaction', token=self.initAccount)
            self.initTransaction = CTransaction(dt.datetime.today()+dt.timedelta(minutes=1), 1)
            _signature_wonabru = self.wallet_first.sign(self.initAtomicTransaction.getHash())
            self.initTransaction.add(self.initAtomicTransaction, '__future__', _signature_wonabru)
            initBlock = self
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

    """
    def save(self):
        if self.kade.get('initAccount') is None:
            self.kade.save('initAccount', self.initAccount.getParameters())
        if self.kade.get('firstAccount') is None:
            self.kade.save('firstAccount', self.firstAccount.getParameters())
            self.kade.save(self.firstAccount.address, self.firstAccount.getParameters())
        if self.kade.get('initTransaction') is None:
            self.kade.save('initTransaction', self.initTransaction.getParameters())
    
 
    def update(self):
        self.initAccount.setParameters(self.kade.get('initAccount'))
        self.firstAccount.setParameters(self.kade.get('firstAccount'))
        self.firstAccount.update()
        self.initTransaction.setParameters(self.kade, self.kade.get('initTransaction'))
        for acc in self.initAccount.chain.uniqueAccounts.keys():
            if acc not in [self.initAccount.address, self.firstAccount.address]:
                _account = CBaseAccount(self.kade, '__temp__', acc)
                try:
                    _account.update(do_update=do_update)
                    self.initAccount.chain.uniqueAccounts[acc] = _account
                except Exception as ex:
                    print(str(ex))
                    return False
    """
