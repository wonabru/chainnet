import numpy as np
import datetime as dt
from transaction import CAtomicTransaction, CTransaction
from limitedToken import CLimitedToken
from initBlock import CInitBlock
from database import CSQLLite
from actionToken import CActionToken
from wallet import CWallet

myWallet = CWallet()
ownAddress = myWallet.pubKey

kade = CSQLLite(ownAddress)
Qcoin = CInitBlock(kade)
baseToken = CLimitedToken(kade, 'Q', 1, 0)
baseToken = baseToken.copyFromBaseLimitToken(Qcoin.getBaseToken())
account_1 = baseToken.copyFromBaseAccount(Qcoin.firstAccount)


actionToken = CActionToken(kade, 'A', 10000, account_1)

accounts = [account_1]
for i in range(100):
    accounts.append(baseToken.create('', accounts[-1]))
    account_1.send(accounts[-1], baseToken, np.random.randint(1,10000))
    
    if i < 50:
        actionToken.atach(accounts[-1], atacher=account_1)
        account_1.send(accounts[-1], actionToken, 200)
        
for i in range(100):
    accounts[1].send(accounts[np.random.randint(0,100)], actionToken, 1)
    
actionToken.showAll()
print(actionToken.accountName, ' Real total supply = ', actionToken.totalSupply)
#Example of Atomic transaction

baseToken.lockAccounts(accounts[2], accounts[3])
baseToken.lockAccounts(accounts[3], accounts[1])
baseToken.lockAccounts(accounts[1], accounts[2])

txn = CTransaction(dt.datetime.strptime('2020-03-29', '%Y-%m-%d'), 3)
atomic_1 = CAtomicTransaction(accounts[2], accounts[3], 1000.00, optData='send TXN', token=baseToken)
atomic_2 = CAtomicTransaction(accounts[3], accounts[1], 100.00, optData='send TXN', token=baseToken)
atomic_3 = CAtomicTransaction(accounts[1], accounts[2], 10.00, optData='send TXN', token=baseToken)
txn.add(atomic_1, 'sign_1', 'sign_2')
txn.add(atomic_2, 'sign_1', 'sign_3')
txn.add(atomic_3, 'sign_1', 'sign_3')

baseToken.showAll()
kade.close()