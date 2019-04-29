import datetime as dt
from baseAccount import CBaseAccount
from baseLimitedToken import CBaseLimitedToken
from transaction import CAtomicTransaction, CTransaction
from wallet import CWallet
from genesis import CGenesis
initBlock = None

class CInitBlock(CGenesis):
    def __init__(self, kade=None, wallet=None):
        global initBlock

        if initBlock is None:
            super().__init__()
            #self.init_wallet = CWallet('init')
            #self.init_wallet.RSAkey = self.getPrivKey()
            self.kade = kade
            self.baseTotalSupply = 23000000.23
            self.initAccount = CBaseLimitedToken(self.kade, 'Q', self.baseTotalSupply, address=self.initAccountPubKey)
            self.initAccount.amount[self.initAccount.address] = self.baseTotalSupply
            self.firstAccount = CBaseAccount(self.kade, 'wonabru', address='1')
            #self.wallet_first = CWallet('wonabru')
            self.firstAccount.address = self.first_accountPubKey # self.wallet_first.pubKey #
            #TODO
            #self.initAccount.chain.uniqueAccounts[self.firstAccount.address] = self.firstAccount
            self.firstAccount.chain.uniqueAccounts[self.initAccount.address] = self.initAccount
            self.initAtomicTransaction = CAtomicTransaction(self.initAccount, self.firstAccount, self.baseTotalSupply, optData='initTransaction', token=self.initAccount, time='2019-04-28 17:00:00')
            _hash = self.initAtomicTransaction.getHash()
            self.initTransaction = CTransaction(dt.datetime(2019, 4, 28, 17, 1, 0), 1)
            _signature_wonabru = self.signature_wonabru # self.wallet_first.sign(_hash)
            _signature_init = self.signature_init  # self.init_wallet.sign(_hash) # #
            self.initTransaction.add(self.initAtomicTransaction, _signature_init, _signature_wonabru)
            initBlock = self
        else:
            self.baseTotalSupply = initBlock.baseTotalSupply
            self.initAccount = initBlock.initAccount
            self.firstAccount = initBlock.firstAccount
            #self.wallet_first = initBlock.wallet_first
            self.initAtomicTransaction = initBlock.initAtomicTransaction
            self.initTransaction = initBlock.initTransaction


    def getInitTransaction(self):
        return self.initTransaction

    def getBaseToken(self):
        return self.initAccount

