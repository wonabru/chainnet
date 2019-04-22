
class CChain():
    def __init__(self):
        self.transactions = []
        self.uniqueAccounts = {}
        #TO DO
        self.accountsCreated = {}


    def getParameters(self):
        return self.uniqueAccounts, self.accountsCreated

    def setParameters(self, par):
        accountsCreated, uniqueAccounts = par
        #self.transactions = transactions
        self.uniqueAccounts = uniqueAccounts
        self.accountsCreated = accountsCreated

    #This should be called when transaction is spread and accepted in blockchain
    def addTransaction(self, transaction):
        if transaction not in self.transactions:
            self.transactions.append(transaction)
            for atomic in transaction.atomicTransactions:
                self.uniqueAccounts[atomic.sender.address] = atomic.sender
                self.uniqueAccounts[atomic.recipient.address] = atomic.recipient

    def get_unique_account_names(self):
        return [acc.accountName for acc in self.uniqueAccounts.values()]
