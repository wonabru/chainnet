from account import CAccount

class CLimitedToken(CAccount):
    def __init__(self, DB, tokenName, totalSupply, creator, address):
        self.creator = 0
        super().__init__(DB, tokenName, creator, address)
        self.totalSupply = totalSupply
        self.owner = creator
        self.owner.setAmount(self, totalSupply)

    def copyFromBaseLimitToken(self, baseLimitToken):
        token = CLimitedToken(self.kade, baseLimitToken.accountName, baseLimitToken.totalSupply,
                              baseLimitToken, address=baseLimitToken.address)
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
