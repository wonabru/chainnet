from baseAccount import CBaseAccount
from initBlock import CInitBlock
from genesis import CGenesis
import time

class CAccount(CBaseAccount):
    def __init__(self, DB, accountName, creator, address):
        self.kade = DB
        super().__init__(DB, accountName, address)
        self.init_block = None
        self.initTransaction = None
        self.creator = creator
        self.init_block = CInitBlock()
        self.chain.uniqueAccounts[CGenesis().initAccountPubKey] = self.init_block.getBaseToken()
        self.initTransaction = self.init_block.getInitTransaction()
        try:
            self.chain.uniqueAccounts[creator.address] = creator
            creator.chain.uniqueAccounts[self.address] = self
            if not isinstance(creator, CBaseAccount):
                creator.save()
        except:
            print('Warning: creator is not valid account')

    def copyFromBaseAccount(self, baseAccount):
        account = CAccount(self.kade, baseAccount.accountName, baseAccount, baseAccount.address)
        account.decimalPlace = baseAccount.decimalPlace
        account.amount = baseAccount.amount
        account.chain = baseAccount.chain
        self.chain.uniqueAccounts[baseAccount.address] = account
        baseAccount.chain.uniqueAccounts[self.address] = self
        return account

    def create(self, accountName, creator, address, save=True):
        if address in self.chain.uniqueAccounts or accountName in self.chain.get_unique_account_names():
            return None
        account = CAccount(self.kade, accountName, creator, address)
        #self.chain.uniqueAccounts[account.address] = account
        #account.chain.uniqueAccounts[self.address] = self
        if save:
            account.save()
            self.save()
            creator.save()
        return account

    def invite(self, accountName, creator, address, save=True):
        from transaction import check_if_common_connection
        self.kade.get('Account:' + address)

        account = CAccount(self.kade, accountName, creator, address)
        account.update_look_at()
        check_if_common_connection(creator, account)

        #self.chain.uniqueAccounts[account.address] = account
        #account.chain.uniqueAccounts[self.address] = self
        if save:
            account.save(announce='DO NOT SAVE LOCAL')
            self.save()
            creator.save()
        return account

    def inviteLimitedToken(self, accountName, creator, address, save=True):
        from transaction import check_if_common_connection
        from limitedToken import CLimitedToken
        self.kade.get('Account:' + address)

        account = CLimitedToken(self.kade, accountName, 0, creator, address)
        while account.accountName.find('__') > 0:
            account.update_look_at()
            time.sleep(1)
        check_if_common_connection(creator, account)

        #self.chain.uniqueAccounts[account.address] = account
        #account.chain.uniqueAccounts[self.address] = self
        if save:
            account.save(announce='DO NOT SAVE LOCAL')
            self.save()
            creator.save()
        return account

    def inviteActionToken(self, accountName, creator, address, save=True):
        from transaction import check_if_common_connection
        from actionToken import CActionToken
        self.kade.get('Account:' + address)

        account = CActionToken(self.kade, accountName, 0, creator, address)
        while account.accountName.find('__') > 0:
            account.update_look_at()
            time.sleep(1)
        check_if_common_connection(creator, account)

        #self.chain.uniqueAccounts[account.address] = account
        #account.chain.uniqueAccounts[self.address] = self
        if save:
            account.save(announce='DO NOT SAVE LOCAL')
            self.save()
            creator.save()
        return account

    def save(self, announce=''):
        super().save(announce)
        
    def update(self, with_chain=True):
        super().update(with_chain=with_chain)

    def update_look_at(self, with_chain=True):
        super().update_look_at(with_chain=with_chain)