from account import CAccount

class CLimitedToken(CAccount):
    def __init__(self, DB, tokenName, totalSupply, creator, address, save=True):
        self.creator = 0
        super().__init__(DB, tokenName, creator, address)
        self.totalSupply = totalSupply
        if creator is None:
            self.owner = CAccount(DB, '__creator__', None, -1)
        else:
            self.owner = creator
            self.owner.setAmount(self, totalSupply, save=save)
        self.setAmount(self, 0, save=save)

    def copyFromBaseLimitToken(self, baseLimitToken):
        token = CLimitedToken(self.kade, baseLimitToken.accountName, baseLimitToken.totalSupply,
                              baseLimitToken, address=baseLimitToken.address)
        token.save()
        return token

    def save(self):
        super().save()
        self.kade.save('limitedToken ' + self.address, [self.totalSupply, self.owner.address])

    def update(self):
        super().update()
        par = self.kade.get('limitedToken ' + self.address)
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
            try:
                self.chain.uniqueAccounts[acc].show()
                totalSupply += self.chain.uniqueAccounts[acc].amount[self.address]
            except:
                pass
        
        return self.accountName + ' total Supply: ' + str(totalSupply)

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
            return [attacher]

        print('Handshake fails, no common connections')
        return None

    def spreadToWorld(self, accounts):
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

        account.setAmount(self, 0, save=False)
        self.chain.uniqueAccounts[account.address] = account
        account.chain.uniqueAccounts[self.address] = self

        listToSpread.append(self)
        listToSpread.append(attacher)
        listToSpread.append(account)
        self.spreadToWorld(listToSpread)

        return True