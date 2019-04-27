import datetime as dt
import pickle
from copy import deepcopy
from wallet import CWallet

class CAtomicTransaction():
    def __init__(self, sender, recipient, amount, optData, token):

        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = 0
        self.optData = ""
        self.time = ""

        if sender.address == recipient.address:
            print('sender cannot be the same as recipient')
            return
        if sender.address not in token.isLocked.keys() and sender.address != '0':
            print('Cannot perform transaction. Lock sender account first')
            return
        if recipient.address not in token.isLocked.keys() and sender.address != '0':
            print('Cannot perform transaction. Lock recipient account first')
            return
        if sender.address != '0' and token.isLocked[sender.address] != recipient.address:
            print('Sender account is locked, but not for the recipient')
            return
        if sender.address != '0' and token.isLocked[recipient.address] != sender.address:
            print('Recipient account is locked, but not for the sender')
            return
        
        list1 = list(sender.chain.uniqueAccounts.keys()) + [sender.address]
        list2 = list(recipient.chain.uniqueAccounts.keys()) + [recipient.address]

        if any(e in list2 for e in list1) == False and sender.address != '0':
            print('sender and recipient have no common connections')
            return
        if recipient.address not in token.chain.uniqueAccounts:
            token.chain.uniqueAccounts[recipient.address] = recipient
        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.optData = optData
        self.time = str(dt.datetime.strftime(dt.datetime.today(), '%Y-%m-%d %H:%M:%S'))

    def getParameters(self):
        _token = self.token.getParameters(with_chain=False)
        _sender = self.sender.getParameters(with_chain=False)
        _recipient = self.recipient.getParameters(with_chain=False)
        return _token, _sender, _recipient, self.amount, self.optData, self.time

    def setParameters(self, par):
        _token, _sender, _recipient, self.amount, self.optData, self.time = par
        self.token.setParameters(_token, with_chain=False)
        self.token.update(with_chain=False)
        self.sender.setParameters(_sender, with_chain=False)
        self.sender.update(with_chain=False)
        self.recipient.setParameters(_recipient, with_chain=False)
        self.recipient.update(with_chain=False)

    def getHash(self):
        return str(hash(pickle.dumps(self.getParameters())))

class CTransaction():
    def __init__(self, timeToClose, noAtomicTransactions):
        self.atomicTransactions = []
        self.signatures = {}
        self.senders = []
        self.recipients = []
        self.timeToClose = str(dt.datetime.strftime(timeToClose, '%Y-%m-%d %H:%M:%S'))
        self.noAtomicTransactions = noAtomicTransactions

    def getParameters(self):
        _atomics = [atomic.getParameters() for atomic in self.atomicTransactions]
        _senders = [sender.getParameters(with_chain=False) for sender in self.senders]
        _recipients = [recipient.getParameters(with_chain=False) for recipient in self.recipients]
        _signatures = str(self.signatures)
        return _atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions

    def setParameters(self, DB, par):
        from account import CAccount
        _atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions = par

        self.signatures = _signatures[:]

        self.senders = []
        for _sender in _senders:
            _temp_sender = CAccount(DB, '__tempTransaction__', None, None, with_initBlock=False)
            _temp_sender.setParameters(_sender, with_chain=False)
            _temp_sender.update(with_chain=False)
            self.senders.append(_temp_sender)

        self.recipients = []
        for _recipient in _recipients:
            _temp_recipient = CAccount(DB, '__tempTransaction__', None, None, with_initBlock=False)
            _temp_recipient.setParameters(_recipient, with_chain=False)
            _temp_recipient.update(with_chain=False)
            self.recipients.append(_temp_recipient)


        self.atomicTransactions = []
        for _atomic in _atomics:
            _temp = CAtomicTransaction(CAccount(DB, '__temp__', None, "", with_initBlock=False),
                                       CAccount(DB, '__temp__', None, "", with_initBlock=False),
                                       0, "",
                                       CAccount(DB, '__temp__', None, "", with_initBlock=False))
            _temp.setParameters(_atomic)
            self.atomicTransactions.append(_temp)


    def add(self, atomicTransaction, signSender, signRecipient):
        
        if self.noAtomicTransactions == len(self.atomicTransactions):
            print('Stack is full. Please first remove one atomicTransaction in order to add new one')
            return 0
        
        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            print('Verification fails')
            return 0
        
        try:
            if dt.datetime.strptime(self.timeToClose, '%Y-%m-%d %H:%M:%S') < dt.datetime.strptime(atomicTransaction.time, '%Y-%m-%d %H:%M:%S'):
                print('Time to finish transaction just elapsed')
                return 0
        except:
            print('AtomicTransaction fails to build')
            return 0
        
        self.atomicTransactions.append(atomicTransaction)
        self.senders.append(atomicTransaction.sender)
        self.recipients.append(atomicTransaction.recipient)
        
        if atomicTransaction.sender not in self.senders and atomicTransaction.sender not in self.recipients:
            self.signatures[atomicTransaction.sender] = signSender
            
        if atomicTransaction.recipient not in self.senders and atomicTransaction.recipient not in self.recipients:
            self.signatures[atomicTransaction.recipient] = signRecipient
        
        if self.noAtomicTransactions == len(self.atomicTransactions):
            if self.checkTransaction() == True:
                for atomic in self.atomicTransactions:
                    if atomic.sender.addAmount(atomic.token, -atomic.amount, False) == False or atomic.recipient.addAmount(atomic.token, atomic.amount, False) == False:
                        print('sender has not enough funds')
                        return False
                    
                    atomic.sender.chain.addTransaction(self)
                    atomic.recipient.chain.addTransaction(self)
                    try:
                        if atomic.sender.address != '0':
                            del atomic.token.isLocked[atomic.sender.address]
                    except:
                        print("Key sender address not found in isLocked")
                    try:
                        if atomic.sender.address != '0':
                            del atomic.token.isLocked[atomic.recipient.address]
                    except:
                        print("Key recipient address not found in isLocked")
                    
                    if atomic.sender.address != '0':
                        return 2
                return 1
            else:
                return 0
        return 1

    def remove(self, atomicTransaction, signSender, signRecipient):
        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            print('Verification fails')
            return False
        
        self.atomicTransactions.remove(atomicTransaction)
        return True

    def checkTransaction(self):
        if self.noAtomicTransactions == 1:
            return True
        for atomic in self.atomicTransactions:
            if atomic.sender in self.recipients and atomic.recipient in self.senders and atomic.sender != atomic.recipient:
                continue
            print('Not a full cycle')
            return False

        return True

    def getHash(self):
        return hash(pickle.dumps(self.getParameters()))

    def verify(self, atomicTransaction, signSender, signRecipient):
        if signSender == '__future__' or CWallet().verify(atomicTransaction.getHash(), signSender, atomicTransaction.sender.address):
            if signRecipient == '__future__' or  CWallet().verify(atomicTransaction.getHash(), signRecipient, atomicTransaction.recipient.address):
                return True
            else:
                print('Recipient signature is not valid')
        else:
            print('Sender signature is not valid')

        return False