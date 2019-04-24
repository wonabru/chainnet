import operator
from account import CAccount

class CActionToken(CAccount):
    def __init__(self, DB, tokenName, initialSupply, creator, address, save=True):
        self.creator = 0
        super().__init__(DB, tokenName, creator, address)
        self.minAmount = 10 ** -self.decimalPlace
        self.totalSupply = initialSupply
        if creator is None:
            self.owner = CAccount(DB, '__creator__', None, -1)
        else:
            self.owner = creator
            self.owner.setAmount(self, initialSupply, save=save)
        self.setAmount(self, 0, save=save)

    def save(self):
        super().save()
        self.kade.save('actionToken ' + self.address, [self.totalSupply, self.owner.address])

    def update(self):
        super().update()
        self.minAmount = 10 ** -self.decimalPlace
        par = self.kade.get('actionToken ' + self.address)
        self.totalSupply, _address = par
        _account = CAccount(self.kade, '__temp__', None, _address)
        _account.update()
        self.owner = _account
        '''
        for acc in self.chain.uniqueAccounts:
            if acc != self.address:
                self.chain.uniqueAccounts[acc].update()
        '''

    def showAll(self):
        self.update()
        totalSupply = 0
        for acc in self.chain.uniqueAccounts:
            self.chain.uniqueAccounts[acc].show()
            totalSupply = totalSupply + self.chain.uniqueAccounts[acc].amount[self.address] \
            if self.address in self.chain.uniqueAccounts[acc].amount.keys() else totalSupply
        
        ret = self.accountName + ' total Supply: ' + str(totalSupply)
        return ret
    
    def handshake(self, account_1, account_2, attacher):
        
        list1 = account_1.chain.uniqueAccounts
        list2 = account_2.chain.uniqueAccounts

        '''
        account = None
        for key, value in list1.items():
            if key in list2:
                account = value
                break
        '''

        if attacher is not None:
            account_1.chain.uniqueAccounts[account_2.address] = account_2
            account_2.chain.uniqueAccounts[account_1.address] = account_1
            #awarded should be oldest connection
            attacher.addAmount(self, self.minAmount, save=False)
            self.totalSupply += self.minAmount
            return [attacher]
        
        print('Handshake fails, no common connections')
        return None
    
    def spreadToWorld(self, accounts):
        #self.update()
        for acc in accounts:
            acc.save()
                
    def attach(self, account, attacher):

        listToSpread = self.handshake(self, account, attacher)
        if listToSpread is None: return False
        if attacher.address == listToSpread[0].address:
            attacher = listToSpread[0]
            listToSpread.remove(attacher)

        if attacher.address not in self.chain.accountsCreated.keys():
            self.chain.accountsCreated[attacher.address] = 1
        else:
            self.chain.accountsCreated[attacher.address] += 1
        
        noCreated = self.chain.accountsCreated[attacher.address] - 1
        
        if attacher.addAmount(self, -(self.minAmount * noCreated), save=False) == False:
            self.chain.accountsCreated[attacher.address] -= 1
            return False
        
        self.totalSupply -= (self.minAmount * noCreated)
        account.setAmount(self, 0, save=False)
        self.chain.uniqueAccounts[account.address] = account
        account.chain.uniqueAccounts[self.address] = self
        
        sorted_pubKey = sorted(self.chain.uniqueAccounts.items(), key=operator.itemgetter(0))
        index_account = sorted_pubKey.index((account.address, account)) - 1
        
        dad = sorted_pubKey[index_account][1]
        dad.addAmount(self, self.minAmount, save=False)
        self.totalSupply += self.minAmount

        listToSpread.append(attacher)
        listToSpread.append(self)
        listToSpread.append(account)

        if dad.address == listToSpread[0].address:
            listToSpread[0] = dad
        else:
            listToSpread.append(dad)

        self.spreadToWorld(listToSpread)
        
        return True