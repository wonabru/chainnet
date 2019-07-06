from sqllite import CDataBase as sqllite
from kademliaGetSet import CDataBase
import socket
from isolated_functions import *

instance_kade = None

class CSQLLite():
    def __init__(self):

        global instance_kade
        if instance_kade is None:
            node_identifier = socket.gethostbyname(socket.gethostname())
            self.sqllite = sqllite()
            self.nodes = ["3.113.39.120", "192.168.0.38", "192.168.56.1", "10.0.2.2", "10.0.2.15", "127.0.0.1", node_identifier]
            self.kade = CDataBase()
            self.kade.initiate()
            instance_kade = self
        else:
            self.nodes = instance_kade.nodes
            self.sqllite = instance_kade.sqllite
            self.kade = instance_kade.kade


    def save(self, key, value, announce=''):
        if isinstance(key, str) == False:
            key = str(key)
        if announce == 'EXTERNAL':
            _current = self.sqllite.get(announce)
            if _current is None:
                self.sqllite.set(key=announce, value=[key, ])
            else:
                _current.append(key)
                _current = list(set(_current))
                self.sqllite.set(key=announce, value=_current)

        else:
            _not_save_local = self.sqllite.get('EXTERNAL')

            if _not_save_local is None: _not_save_local = []

            if not (key in _not_save_local and announce == 'Account:'):
                self.sqllite.set(key=announce + key, value=value)

                if announce != '':
                    self.announce(announce + key, value)
        return self.sqllite.get(announce + key)

    def get(self, key):
        if isinstance(key, str) == False: key = str(key)
        return self.sqllite.get(key=key)

    def announce(self, key, value):
        print('KADEMLIA SET: ',key,' = ',self.kade.set(key=key, value=str(value)))

    def look_at(self, key):
        if isinstance(key, str) == False: key = str(key)
        response = self.kade.get(key=key)

        if response is not None:
            #self.save(key, response)
            try:
                response = str2obj(response)
            except:
                pass
        return response

    def close(self):
        self.sqllite.close()

    def register_node(self, address):
        if address not in self.nodes:
            self.nodes.append(address)

    def bootstrapNodes(self):
        self.kade.bootstrap(self.nodes)
