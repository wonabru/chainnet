import datetime as dt
  
class CAtomicTransaction():
    def __init__(self, sender, recipient, amount, optData, token):
        
        if sender.address == recipient.address:
            print('sender cannot be the same as recipient')
            return None
        if sender.address not in token.isLocked.keys() and sender.address != '0':
            print('Cannot perform transaction. Lock sender account first')
            return None
        if recipient.address not in token.isLocked.keys() and sender.address != '0':
            print('Cannot perform transaction. Lock recipient account first')
            return None        
        if sender.address != '0' and token.isLocked[sender.address] != recipient.address:
            print('Sender account is locked, but not for the recipient')
            return None
        if sender.address != '0' and token.isLocked[recipient.address] != sender.address:
            print('Recipient account is locked, but not for the sender')
            return None
        
        list1 = sender.chain.uniqueAccounts
        list2 = recipient.chain.uniqueAccounts

        if any(e in list2 for e in list1) == False and sender.address != '0':
            print('sender and recipient have no common connections')
            return None
        if recipient.address not in token.chain.uniqueAccounts:
            token.chain.uniqueAccounts[recipient.address] = recipient
        self.token = token
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.optData = optData
        self.time = str(dt.datetime.strftime(dt.datetime.today(), '%Y-%m-%d %H:%M:%S'))
        

class CTransaction():
    def __init__(self, timeToClose, noAtomicTransactions):
        self.atomicTransactions = []
        self.signatures = {}
        self.senders = []
        self.recipients = []
        self.timeToClose = timeToClose
        self.noAtomicTransactions = noAtomicTransactions

    def add(self, atomicTransaction, signSender, signRecipient, save=True):
        
        if self.noAtomicTransactions == len(self.atomicTransactions):
            print('Stack is full. Please first remove one atomicTransaction in order to add new one')
            return False
        
        if self.verify(atomicTransaction, signSender, signRecipient) == False:
            print('Verification fails')
            return False
        
        try:
            if self.timeToClose < dt.datetime.strptime(atomicTransaction.time, '%Y-%m-%d %H:%M:%S'):
                print('Time to finish transaction just elapsed')
                return False
        except:
            print('AtomicTransaction fails to build')
            return False
        
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
                    if atomic.sender.addAmount(atomic.token, -atomic.amount, save) == False or atomic.recipient.addAmount(atomic.token, atomic.amount, save) == False:
                        print('sender has not enough funds')
                        return False
                    
                    atomic.sender.chain.addTransaction(self)
                    atomic.sender.save()
                    atomic.recipient.chain.addTransaction(self)
                    atomic.recipient.save()
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
                    self.spreadTransactionToWorld()
                return True
            else:
                return False
        return True

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
    '''
    def getHash(self):
        import pickle
        return hash(pickle.dumps(str(self.getParameters())))
    '''
    def spreadTransactionToWorld(self):
        if len(self.atomicTransactions) == 1:
            self.senders[0].kade.save(self.senders[0].address, self.senders[0].getParameters())
            self.recipients[0].kade.save(self.recipients[0].address, self.recipients[0].getParameters())
        else:
            for acc in self.senders:
                acc.kade.save(acc.address, acc.getParameters())

    def verify(self, atomicTransaction, signSender, signRecipient):
        return True