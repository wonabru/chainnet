import numpy as np

class CChain():
    def __init__(self):
        self.transactions = []
        self.uniqueAccounts = {}
        #TO DO
        self.accountsCreated = []
        
    #This should be called when transaction is spread and accepted in blockchain
    def addTransaction(self, transaction):
        if transaction not in self.transactions:
            self.transactions.append(transaction)
            for atomic in transaction.atomicTransactions:
                self.uniqueAccounts[atomic.sender.address] = atomic.sender
                self.uniqueAccounts[atomic.recipient.address] = atomic.recipient
