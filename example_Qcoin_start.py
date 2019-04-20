import datetime as dt
from account import CAccount
from transaction import CAtomicTransaction, CTransaction
from limitedToken import CLimitedToken
from initBlock import CInitBlock

Qcoin = CInitBlock()
account_2 = CAccount('second', Qcoin.firstAccount)

account_3 = CAccount('third', Qcoin.firstAccount)

#Example of Atomic transaction
atomic_2 = CAtomicTransaction(Qcoin.firstAccount, account_2, 1000.00, optData='send TXN')
txn = CTransaction(dt.datetime.strptime('2019-03-24', '%Y-%m-%d'), 1)
if txn.add(atomic_2, 'sign_1', 'sign_2') == True:
    print('Current amount of Q on ', account_2.accountName, ' = ', account_2.amount)
    print('Current amount of Q on', Qcoin.firstAccount.accountName, ' = ', Qcoin.firstAccount.amount)
atomic_3 = CAtomicTransaction(Qcoin.firstAccount, account_3, 100.00, optData='send TXN')
txn = CTransaction(dt.datetime.strptime('2019-03-24', '%Y-%m-%d'), 1)
if txn.add(atomic_3, 'sign_1', 'sign_3') == True:
    print('Current amount of Q on ', account_3.accountName, ' = ', account_3.amount)
    print('Current amount of Q on', Qcoin.firstAccount.accountName, ' = ', Qcoin.firstAccount.amount)
    
account_2.send(account_3, 100)
account_3.send(Qcoin.firstAccount, 100)