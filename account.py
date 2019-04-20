import numpy as np

class CAccount():
    def __init__(self, accountNumber):
        self.minAmount = 0.01
        self.amount = 0
        self.accountNumber = accountNumber
        self.uniqueAccounts = []
        self.pubKey = np.random.randint(1,1000000000)
        #self.transactions = []

    def setAmount(self, amount):
        self.amount = amount
        self.amount = np.round(self.amount / self.minAmount) * self.minAmount

    def addAmount(self, amount):
        self.amount += amount
        self.amount = np.round(self.amount / self.minAmount) * self.minAmount