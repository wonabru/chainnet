import datetime as dt
import pickle
from Crypto import Hash
from wallet import CWallet, serialize
from genesis import CGenesis



def check_if_common_connection(sender, recipient):
    list1 = list(sender.chain.uniqueAccounts.keys()) + [sender.address]
    list2 = list(recipient.chain.uniqueAccounts.keys()) + [recipient.address]

    if any(e in list2 for e in list1) == False and sender.address != CGenesis().initAccountPubKey:
        raise Exception('Atomic transaction', 'sender and recipient have no common connections')

    return True

class CAtomicTransaction():
    def __init__(self, sender, recipient, amount, optData, token, time=None):

        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = 0
        self.optData = ""
        self.time = ""
        if amount < 0:
            return

        if sender.address == recipient.address:
            raise Exception('Atomic transaction', 'sender cannot be the same as recipient')

        if sender.address not in token.isLocked.keys() and sender.address != CGenesis().initAccountPubKey:
            raise Exception('Atomic transaction', 'Cannot perform transaction. Lock sender account first')

        if recipient.address not in token.isLocked.keys() and sender.address != CGenesis().initAccountPubKey:
            raise Exception('Atomic transaction', 'Cannot perform transaction. Lock recipient account first')

        if sender.address != CGenesis().initAccountPubKey and token.isLocked[sender.address] != recipient.address:
            raise Exception('Atomic transaction', 'Sender account is locked, but not for the recipient')

        if sender.address != CGenesis().initAccountPubKey and token.isLocked[recipient.address] != sender.address:
            raise Exception('Atomic transaction', 'Recipient account is locked, but not for the sender')

        
        check_if_common_connection(sender, recipient)

        if recipient.address not in token.chain.uniqueAccounts:
            token.chain.uniqueAccounts[recipient.address] = recipient
        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.optData = optData
        if time is None:
            self.time = str(dt.datetime.strftime(dt.datetime.today(), '%Y-%m-%d %H:%M:%S'))
        else:
            self.time = time

    def getParameters(self):
        _token = self.token.getParameters(with_chain=False)
        _sender = self.sender.getParameters(with_chain=False)
        _recipient = self.recipient.getParameters(with_chain=False)
        return [_token, _sender, _recipient, self.amount, self.optData, self.time]

    def setParameters(self, par):
        _token, _sender, _recipient, self.amount, self.optData, self.time = par
        self.token.setParameters(_token, with_chain=False)
        self.token.update(with_chain=False)
        self.sender.setParameters(_sender, with_chain=False)
        self.sender.update(with_chain=False)
        self.recipient.setParameters(_recipient, with_chain=False)
        self.recipient.update(with_chain=False)

    def get_for_hash(self):
        _token = self.token.address
        _sender = self.sender.address
        _recipient = self.recipient.address
        return _token + _sender + _recipient + str(self.amount) + str(self.optData) + self.time

    def getHash(self):
        digest = Hash.SHA256.new()
        digest.update(serialize(self.get_for_hash()))
        return digest.hexdigest()

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
        return [_atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions]

    def get_for_hash(self):
        _atomics = [atomic.get_for_hash() for atomic in self.atomicTransactions]
        _senders = [sender.address for sender in self.senders]
        _recipients = [recipient.address for recipient in self.recipients]
        _signatures = str(self.signatures)
        return _atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions

    def setParameters(self, DB, par):
        from account import CAccount
        import ast

        _atomics, _signatures, _senders, _recipients, self.timeToClose, self.noAtomicTransactions = \
            self.atomicTransactions[0].sender.verify(par)

        response = {}
        try:
            response = ast.literal_eval(_signatures.replace('true', 'True').replace('false', 'False'))
        except:
            pass
        self.signatures = response

        self.senders = []
        for _sender in _senders:
            _temp_sender = CAccount(DB, '__tempTransaction__', None, None)
            _temp_sender.setParameters(_sender, with_chain=False)
            _temp_sender.update(with_chain=False)
            self.senders.append(_temp_sender)

        self.recipients = []
        for _recipient in _recipients:
            _temp_recipient = CAccount(DB, '__tempTransaction__', None, None)
            _temp_recipient.setParameters(_recipient, with_chain=False)
            _temp_recipient.update(with_chain=False)
            self.recipients.append(_temp_recipient)


        self.atomicTransactions = []
        for _atomic in _atomics:
            _temp = CAtomicTransaction(CAccount(DB, '__temp__', None, ""),
                                       CAccount(DB, '__temp__', None, ""),
                                       -1, "",
                                       CAccount(DB, '__temp__', None, ""))
            _temp.setParameters(_atomic)
            self.atomicTransactions.append(_temp)


    def add(self, atomicTransaction, signSender, signRecipient):
        
        if self.noAtomicTransactions == len(self.atomicTransactions):
            raise Exception('Add Transaction',
                            'Stack is full. Please first remove one atomicTransaction in order to add new one')

        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            raise Exception('Add Transaction', 'Verification fails')

        
        try:
            if dt.datetime.strptime(self.timeToClose, '%Y-%m-%d %H:%M:%S') < dt.datetime.strptime(atomicTransaction.time, '%Y-%m-%d %H:%M:%S'):
                raise Exception('Add Transaction', 'Time to finish transaction just elapsed')

        except:
            raise Exception('Add Transaction', 'AtomicTransaction fails to build')

        
        self.atomicTransactions.append(atomicTransaction)
        self.senders.append(atomicTransaction.sender)
        self.recipients.append(atomicTransaction.recipient)
        
        self.signatures[atomicTransaction.sender.address] = signSender
            
        self.signatures[atomicTransaction.recipient.address] = signRecipient
        
        if self.noAtomicTransactions == len(self.atomicTransactions):
            if self.checkTransaction() == True:
                for atomic in self.atomicTransactions:
                    if atomic.sender.addAmount(atomic.token, -atomic.amount, False) == False or atomic.recipient.addAmount(atomic.token, atomic.amount, False) == False:
                        raise Exception('Add Transaction','sender has not enough funds')

                    
                    atomic.sender.chain.addTransaction(self)
                    atomic.recipient.chain.addTransaction(self)
                    try:
                        if atomic.sender.address != CGenesis().initAccountPubKey:
                            del atomic.token.isLocked[atomic.sender.address]
                    except:
                        raise Exception('Add Transaction', "Key sender address not found in isLocked")
                    try:
                        if atomic.sender.address != CGenesis().initAccountPubKey:
                            del atomic.token.isLocked[atomic.recipient.address]
                    except:
                        raise Exception('Add Transaction', "Key recipient address not found in isLocked")
                    
                    if atomic.sender.address != CGenesis().initAccountPubKey:
                        return 2
                return 1
            else:
                return 0
        return 1

    def remove(self, atomicTransaction, signSender, signRecipient):
        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            raise Exception('Remove Transaction', 'Verification fails')

        self.atomicTransactions.remove(atomicTransaction)
        return True

    def checkTransaction(self):
        if self.noAtomicTransactions == 1:
            return True
        for atomic in self.atomicTransactions:
            if atomic.sender in self.recipients and atomic.recipient in self.senders and atomic.sender != atomic.recipient:
                continue
            raise Exception('Check Transaction','Not a full cycle')
        return True

    def getHash(self):
        digest = Hash.SHA256.new()
        digest.update(serialize(self.get_for_hash()))
        return digest.hexdigest()

    def verify(self, atomicTransaction, signSender, signRecipient):
        if signSender == '__future__' or CWallet().verify(atomicTransaction.getHash(), signSender, atomicTransaction.sender.address):
            if signRecipient == '__future__' or  CWallet().verify(atomicTransaction.getHash(), signRecipient, atomicTransaction.recipient.address):
                return True
            else:
                raise Exception('Verify Transaction', 'Recipient signature is not valid')
        else:
            raise Exception('Verify Transaction', 'Sender signature is not valid')
