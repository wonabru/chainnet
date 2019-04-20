from account import CAccount

class CLimitedToken(CAccount):
    def __init__(self, DB, tokenName, totalSupply, creator):
        self.creator = 0
        super().__init__(DB, tokenName, creator)
        self.totalSupply = totalSupply
        if creator == 0:
            self.owner = CAccount(DB)
        else:
            self.owner = creator
        self.owner.setAmount(self, totalSupply)

    def copyFromBaseLimitToken(self, baseLimitToken):
        token = CLimitedToken(self.kade, baseLimitToken.accountName, baseLimitToken.totalSupply, baseLimitToken)
        token.address = baseLimitToken.address
        token.save()
        return token

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
            totalSupply += self.chain.uniqueAccounts[acc].amount[self.address]
        
        print(self.accountName, ' total Supply: ', totalSupply)
