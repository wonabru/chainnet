import numpy as np
from chain import CChain
from baseAccount import CBaseAccount
from initBlock import CInitBlock


class CCreator(CBaseAccount):
    pass

class CAccount(CBaseAccount):
    def __init__(self, DB, accountName = '', creator = 0, wallet = None):
        self.kade = DB
        super().__init__(DB, accountName, wallet)
        
        if creator == 0:
            self.creator = CCreator(self.kade)
            self.creator.address = np.random.randint(1,1000000000)
        else:
            self.creator = creator
        self.initTransaction = CInitBlock(self.kade).getInitTransaction()
        try:
            self.chain.uniqueAccounts[creator.address] = creator
        except:
            print('Warning: creator is not valid account')

        self.save()

    def copyFromBaseAccount(self, baseAccount):
        account = self.create(baseAccount.accountName, baseAccount)
        account.decimalPlace = baseAccount.decimalPlace
        account.amount = baseAccount.amount
        account.address = baseAccount.address
        account.chain = baseAccount.chain
        account.save()
        
        return account

    def create(self, accountName, creator):
        account = CAccount(self.kade, accountName, creator)
        self.chain.uniqueAccounts[0] = CInitBlock(self.kade).getBaseToken()
        self.chain.uniqueAccounts[account.address] = account
        account.save()
        return account

    def save(self):
        super().save()
        
    def update(self):
        super().update()

