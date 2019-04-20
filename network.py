import numpy as np
from account import CAccount
from transaction import CTransaction, CAtomicTransaction

class CNetwork():
    def __init__(self):
        self.totalSupply = 0
        accountInit = CAccount(0)
        accountInit.pubKey = 0
        self.accounts = [accountInit, ]
        self.minAmount = accountInit.minAmount
        self.numberOfAccounts = 0
        self.transactions = []

    def initNetwork(self):
        self.numberOfAccounts += 1
        account_temp = CAccount(self.numberOfAccounts)
        account_temp.setAmount(self.minAmount)
        self.accounts.append(account_temp)

    def createshake(self, sender, recipient, hash):
        transaction = CTransaction()
        transaction.add(CAtomicTransaction(sender, recipient, 0.0, hash))
        transaction.add(CAtomicTransaction(recipient, sender, 0.0, hash))
        self.createTransaction(transaction)

    def handshake(self, sender, recipient):
        transaction = CTransaction()
        transaction.add(CAtomicTransaction(sender, recipient, 0.0, self.findShortestPath(sender, recipient)))
        transaction.add(CAtomicTransaction(recipient, sender, 0.0, self.findShortestPath(sender, recipient)))
        self.createTransaction(transaction)

    def previousPubKeyAccount(self, pubKey):
        minDistance = 1000000000
        previousAccount = None
        for account in self.accounts:
            if pubKey - account.pubKey < minDistance and pubKey - account.pubKey > 0:
                minDistance = pubKey - account.pubKey
                previousAccount = account

        return previousAccount

    def createAccount(self, creator):
        if creator in self.accounts:
            #if creator.amount < self.minAmount:
            #    print('not enough Q in account')
            #    return None



            self.numberOfAccounts += 1
            account_temp = CAccount(self.numberOfAccounts)
            self.accounts.append(account_temp)

            previousAccount = self.previousPubKeyAccount(account_temp.pubKey)
            if previousAccount is not None:
                self.accounts[previousAccount.accountNumber].addAmount(self.minAmount)
            else:
                print('Previous Account Public Key is not existing')
            createhash = np.random.randint(1, 1000000000)
            self.createshake(creator, account_temp, createhash)
            self.accounts[creator.accountNumber].addAmount(-self.minAmount)
            return self.accounts[-1]
        else:
            print('no such creator in network')
            return None

    def checkAccount(self, accountNumber):
        return True if accountNumber <= self.numberOfAccounts else False

    def createTransaction(self, transaction):
        if len(transaction.atomicTransactions) == 0:
            print('no atomic transactions in block')
            return None
        if transaction.checkTransaction() == False:
            print('check transaction method fails')
            return None
        for atomic in transaction.atomicTransactions:
            if atomic.sender.amount < atomic.amount:
                print('Not enough Q in account %d to create transaction' % atomic.sender.accountNumber)
                return None
            if self.checkAccount(atomic.sender.accountNumber) == False or self.checkAccount(atomic.recipient.accountNumber) == False:
                print('Account %d or %d not in Q coin network' % (atomic.sender.accountNumber, atomic.recipient.accountNumber))
                return None

        for atomic in transaction.atomicTransactions:

            if atomic.recipient.accountNumber not in self.accounts[atomic.sender.accountNumber].uniqueAccounts:
                #if atomic.amount >= self.minAmount:
                self.accounts[atomic.sender.accountNumber].uniqueAccounts.append(atomic.recipient.accountNumber)
                self.accounts[atomic.recipient.accountNumber].uniqueAccounts.append(atomic.sender.accountNumber)
                self.accounts[atomic.sender.accountNumber].addAmount(self.minAmount)

            self.accounts[atomic.sender.accountNumber].addAmount(-atomic.amount)
            self.accounts[atomic.recipient.accountNumber].addAmount(atomic.amount)
            #self.accounts[atomic.sender.accountNumber].transactions.append(transaction)

        self.transactions.append(transaction)

    def getAccount(self, numberAccount):
        return self.accounts[numberAccount]

    def getRndAccount(self):
        return self.accounts[np.random.randint(1, self.numberOfAccounts)]

    def getTotalSupply(self):
        self.totalSupply = 0
        for account in self.accounts:
            self.totalSupply += account.amount
        return self.totalSupply

    def getTransactionHash(self, sender, recipient):
        participants = [sender.accountNumber, recipient.accountNumber]
        hashes = [[tr.hash for tr in transaction.atomicTransactions if tr.sender.accountNumber in participants or tr.recipient.accountNumber in participants]
         for transaction in self.transactions]

        if len(hashes) > 0:
            return hashes[0]

        return None

    def findShortestPath(self, sender, recipient):
        if recipient.accountNumber in self.accounts[sender.accountNumber].uniqueAccounts:
            if sender.accountNumber in self.accounts[recipient.accountNumber].uniqueAccounts:
                return [self.getTransactionHash(sender, recipient)]

        for proxy in self.accounts[sender.accountNumber].uniqueAccounts:
            if proxy in self.accounts[recipient.accountNumber].uniqueAccounts:
                return [self.getTransactionHash(sender, self.accounts[proxy]),
                        self.getTransactionHash(self.accounts[proxy], recipient)]

        return None



