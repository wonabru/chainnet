import operator
from account import CAccount

class CActionToken(CAccount):
    def __init__(self, DB, tokenName, initialSupply, creator, wallet = None):
        self.creator = 0
        super().__init__(DB, tokenName, creator, wallet)
        self.minAmount = 10 ** -self.decimalPlace
        self.totalSupply = initialSupply
        if creator == 0:
            self.owner = CAccount(DB)
        else:
            self.owner = creator
        self.owner.setAmount(self, initialSupply)

    def update(self):
        super().update()
        for acc in self.chain.uniqueAccounts:
            if acc != self.address:
                self.chain.uniqueAccounts[acc].update()
        
    def showAll(self):
        self.update()
        totalSupply = 0
        for acc in self.chain.uniqueAccounts:
            self.chain.uniqueAccounts[acc].show()
            totalSupply = totalSupply + self.chain.uniqueAccounts[acc].amount[self.address] \
            if self.address in self.chain.uniqueAccounts[acc].amount.keys() else totalSupply
        
        print(self.accountName, ' total Supply: ', totalSupply)
        return totalSupply
    
    def handshake(self, account_1, account_2):
        
        list1 = account_1.chain.uniqueAccounts
        list2 = account_2.chain.uniqueAccounts
        
        account = None
        for key, value in list1.items():
            if key in list2:
                account = value
                break
        
        if account is not None:
            account_1.chain.uniqueAccounts[account_2.address] = account_2
            account_2.chain.uniqueAccounts[account_1.address] = account_1
            #awarded should be oldest connection
            account.addAmount(self, self.minAmount)
            self.totalSupply += self.minAmount
            return [account_1, account_2, account]
        
        print('Handshake fails, no common connections')
        return None
    
    def spreadToWorld(self, accounts):
        for acc in accounts:
            acc.kade.save(acc.address, acc.getParameters())
                
    def atach(self, account, atacher):
        

        listToSpread = self.handshake(self, account)
        if listToSpread is None: return False
        
        if atacher.address not in self.chain.accountsCreated.keys():
            self.chain.accountsCreated[atacher.address] = 1
        else:
            self.chain.accountsCreated[atacher.address] += 1
        
        noCreated = self.chain.accountsCreated[atacher.address] - 1
        
        if atacher.addAmount(self, -(self.minAmount * noCreated)) == False:
            self.chain.accountsCreated[atacher.address] -= 1
            return False
        
        self.totalSupply -= (self.minAmount * noCreated)
        account.amount[self.address] = 0
        self.chain.uniqueAccounts[account.address] = account
        account.chain.uniqueAccounts[self.address] = self
        
        sorted_pubKey = sorted(self.chain.uniqueAccounts.items(), key=operator.itemgetter(0))
        index_account = sorted_pubKey.index((account.address, account)) - 1
        
        dad = sorted_pubKey[index_account][1]
        dad.addAmount(self, self.minAmount)
        self.totalSupply += self.minAmount
        
        listToSpread.append(self)
        listToSpread.append(atacher)
        listToSpread.append(dad)
        listToSpread.append(account)
        self.spreadToWorld(listToSpread)
        
        return True