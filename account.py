import numpy as np
from chain import CChain
from baseAccount import CBaseAccount
from initBlock import CInitBlock
from baseLimitedToken import CBaseLimitedToken

class CAccount(CBaseAccount):
    def __init__(self, DB, accountName, creator, address):
        self.kade = DB
        super().__init__(DB, accountName, address)

        self.init_block = None
        self.initTransaction = None
        self.creator = creator
        self.init_block = CInitBlock()
        self.chain.uniqueAccounts['0'] = self.init_block.getBaseToken()
        self.initTransaction = self.init_block.getInitTransaction()
        try:
            self.chain.uniqueAccounts[creator.address] = creator
            creator.chain.uniqueAccounts[self.address] = self
            if not isinstance(creator, CBaseAccount):
                creator.save()
        except:
            print('Warning: creator is not valid account')

    def copyFromBaseAccount(self, baseAccount):
        account = self.create(baseAccount.accountName, baseAccount, baseAccount.address, save=False)
        account.decimalPlace = baseAccount.decimalPlace
        account.amount = baseAccount.amount
        account.chain = baseAccount.chain

        return account

    def create(self, accountName, creator, address, save=True):
        if address in self.chain.uniqueAccounts or accountName in self.chain.get_unique_account_names():
            return None
        account = CAccount(self.kade, accountName, creator, address)
        self.chain.uniqueAccounts[account.address] = account
        account.chain.uniqueAccounts[self.address] = self
        if save:
            account.save()
            self.save()
            creator.save()
        return account

    def save(self):
        super().save()
        
    def update(self, with_chain=True):
        super().update(with_chain=with_chain)

