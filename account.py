import numpy as np
from chain import CChain
from baseAccount import CBaseAccount
from initBlock import CInitBlock


class CCreator(CBaseAccount):
    pass

class CAccount(CBaseAccount):
    def __init__(self, DB, accountName, creator, address):
        self.kade = DB
        super().__init__(DB, accountName, address)
        
        self.creator = creator
        self.initTransaction = CInitBlock(self.kade).getInitTransaction()
        try:
            self.chain.uniqueAccounts[creator.address] = creator
        except:
            print('Warning: creator is not valid account')

        self.save()

    def copyFromBaseAccount(self, baseAccount):
        account = self.create(baseAccount.accountName, baseAccount, baseAccount.address)
        account.decimalPlace = baseAccount.decimalPlace
        account.amount = baseAccount.amount
        account.chain = baseAccount.chain
        account.save()
        
        return account

    def create(self, accountName, creator, address):
        if address in self.chain.uniqueAccounts or accountName in self.chain.get_unique_account_names():
            return None
        account = CAccount(self.kade, accountName, creator, address)
        self.chain.uniqueAccounts[0] = CInitBlock(self.kade).getBaseToken()
        self.chain.uniqueAccounts[account.address] = account
        account.save()
        return account

    def save(self):
        super().save()
        
    def update(self):
        super().update()

