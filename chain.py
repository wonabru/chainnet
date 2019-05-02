
class CChain():
    def __init__(self):
        self.transactions = {}
        self.uniqueAccounts = {}
        self.accountsCreated = {}


    def getParameters(self):
        return self.uniqueAccounts, self.accountsCreated, self.transactions

    def setParameters(self, par):
        accountsCreated, uniqueAccounts, transactions = par
        self.transactions = transactions
        self.uniqueAccounts = uniqueAccounts
        self.accountsCreated = accountsCreated

    #This should be called when transaction is spread and accepted in blockchain
    def addTransaction(self, transaction):
        if transaction.getHash() in self.transactions.keys():
            print('Add transaction: ', 'The transaction just was added before')
            return

        self.transactions[transaction.getHash()] = transaction
        for atomic in transaction.atomicTransactions:
            self.uniqueAccounts[atomic.sender.address] = atomic.sender
            self.uniqueAccounts[atomic.recipient.address] = atomic.recipient



    def get_unique_account_names(self):
        return [acc.accountName for acc in self.uniqueAccounts.values()]
