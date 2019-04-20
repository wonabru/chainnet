import numpy as np

class CAtomicTransaction():
    def __init__(self, sender, recipient, amount, hash):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.hash = hash

class CTransaction():
    def __init__(self):
        self.atomicTransactions = []
        self.senders = []
        self.recipients = []

    def add(self, atomicTransaction):
        if atomicTransaction.hash is None:
            print('No Hash of the path')
            return
        self.atomicTransactions.append(atomicTransaction)
        self.senders.append(atomicTransaction.sender)
        self.recipients.append(atomicTransaction.recipient)

    def checkTransaction(self):

        for atomic in self.atomicTransactions:
            if atomic.sender in self.recipients and atomic.recipient in self.senders and atomic.sender != atomic.recipient:
                continue
            print('Not the full cycle')
            return False

        return True

