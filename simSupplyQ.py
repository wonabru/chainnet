from __future__ import division
import numpy as np
import matplotlib.pyplot as plt
import math
import networkx as nx
import matplotlib as mpl
import collections

from network import CNetwork

if __name__ == '__main__':
    QCoin = CNetwork()
    QCoin.initNetwork()
    creator = QCoin.getAccount(1)

    counts = 30

    totalSupply = []
    totalAccountsNumber = []
    maxTotalSupply = []
    for i in range(counts):
        creator = QCoin.getAccount(np.random.randint(1, QCoin.numberOfAccounts)
                                   if QCoin.numberOfAccounts > 1 else 1)
        account_temp = QCoin.createAccount(creator)
        if account_temp is None:
            continue

        [QCoin.handshake(QCoin.getRndAccount(), QCoin.getRndAccount()) for a in range(int(QCoin.numberOfAccounts/3))]

        totalSupply.append(QCoin.getTotalSupply())
        maxTotalSupply.append(QCoin.numberOfAccounts * (QCoin.numberOfAccounts  - 1)/100)
        totalAccountsNumber.append(QCoin.numberOfAccounts)
        if i%10 == 0:
            print('%.2f %% done' % (i/counts * 100))
    qInAccounts = np.transpose(np.array([[a.accountNumber, a.amount] for a in QCoin.accounts]))

    '''
    plt.subplot(131)
    plt.plot(range(QCoin.numberOfAccounts - 1), maxTotalSupply)
    plt.plot(range(QCoin.numberOfAccounts - 1), totalSupply)
    plt.plot(range(QCoin.numberOfAccounts - 1), np.array(totalAccountsNumber)/100)
    plt.ylabel('Total Supply [Q] (Min/Random/Max)')
    plt.xlabel('Time in number of created accounts')
    plt.subplot(132)
    plt.hist(qInAccounts[1], bins=1000)
    plt.title("Q distribution among accounts")
    plt.xlabel('Amount [Q]')
    plt.ylabel('Number of appearance')
    plt.subplot(133)
    plt.plot(qInAccounts[0], qInAccounts[1], 'g.')
    plt.title("Accounts' net values against their age")
    plt.xlabel('Age of account')
    plt.ylabel('Amount [Q]')
    plt.show()
    '''
    G = nx.Graph()
    nodes = []
    for transaction in QCoin.transactions:
        for tr in transaction.atomicTransactions:
            nodes.append((tr.sender.accountNumber, tr.recipient.accountNumber))
    G.add_edges_from(nodes)
    node_sizes = [qInAccounts[1][i] * 200 for i, x in enumerate(qInAccounts[0])]
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  # degree sequence
    # print "Degree sequence", degree_sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.subplot(121)
    plt.bar(deg, cnt, width=0.80, color='b')

    plt.title("Degree Histogram")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    plt.subplot(122)
    plt.hist(qInAccounts[1], bins=counts)

    plt.title("Q distribution among accounts")
    plt.xlabel('Amount [Q]')
    plt.ylabel('Count')
    ax.set_xticks([d + 0.4 for d in deg])
    ax.set_xticklabels(deg)

    # draw graph in inset
    plt.axes([0.4, 0.4, 0.5, 0.5])
    Gcc = sorted(nx.connected_component_subgraphs(G), key=len, reverse=True)[0]
    pos = nx.spring_layout(G)
    plt.axis('off')
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes)
    nx.draw_networkx_edges(G, pos, alpha=0.4)

    plt.show()
    G = nx.DiGraph()
    G.add_edges_from(nodes)

    M = G.number_of_edges()
    edge_colors = range(2, M + 2)
    edge_alphas = [(5 + i) / (M + 4) for i in range(M)]

    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='red')
    edges = nx.draw_networkx_edges(G, pos, node_size=node_sizes, arrowstyle='->',
                                   arrowsize=7, edge_color='green',
                                   width=0.3)
    ax = plt.gca()
    ax.set_axis_off()

    plt.show()
    nx.write_graphml(G, 'Qcoin.graphml')